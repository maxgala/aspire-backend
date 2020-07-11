import json
from chat import *
from base import Session

client = boto3.client('cognito-idp')

credit_costs = {ChatType(1): 5, ChatType(2): 3, ChatType(3): 5}

def handler(event, context):  
    # ----------------- User validation ------------------
    try:
        access_token = (event['headers']['Authorization']).replace('Bearer ', '')
    except:
        return {
        "statusCode": 401,
        "body": json.dumps({
            "message": "Authorization header is expected"
        }),
    }
    
    getuserresponse = client.get_user(
            AccessToken=access_token
        )

    user_att = getuserresponse['UserAttributes']
    error_message = "Insufficient data - {} not specified"
    
    for att in user_att:
        if att['Name'] == 'custom:user_type':
            user_type = att['Value']
        try:
            if att['Name'] == 'custom:membership_type':
                mem_type = att['Value']
        except:
            return {
                "statusCode": 400,
                "body": json.dumps({
                "message": error_message.format("membership type")
                })
            }
        try:
            if att['Name'] == 'custom:credits':
                credit = int(att['Value'])
        except:
            return {
                "statusCode": 400,
                "body": json.dumps({
                "message": error_message.format("credits available")
                })
            }

    if user_type == "Mentor":
        return{
            "statusCode": 409,
            "body": json.dumps({
            "message": "Invalid user type. Senior executives may not reserve chats."
            })
        }
    # ----------------------- End user validation ------------------------------
    # user is mentee
    
    info = json.loads(event["body"])
    chat_id = event["pathParameters"]["chatId"]
    
    session = Session()
    chat = session.query(Chat).get(chat_id)
    credit_cost = credit_costs[chat.chat_type]
    
    sufficient_credits = credit >= credit_cost

    
    if chat != None:
        if not sufficient_credits:
            session.close()
            return {
                "statusCode": 200,
                "body": json.dumps({
                "message": "Insufficient credits, need {} but only have {}".format(credit_cost, credit)
                })
            }
        if not (chat.chat_status == ChatStatus(1) or chat.chat_status == ChatStatus(2)):
            # cannot reserve this chat
            session.close()
            return {
                "statusCode": 409,
                "body": json.dumps({
                "message": "Chat with ID {} cannot be reserved, chat status is {}".format(chat.chat_id,
                                                                                        chat.chat_status)
                })
            }
        
        
        response = client.update_user_attributes(
            UserAttributes=[
                {
                    'Name': 'custom:credits',
                    'Value': str(int(credit) - credit_cost)
                },
            ],
            AccessToken=access_token
        )
        # credits updated, then chat row modified
        
        chat.aspiring_professionals.append(getuserresponse["UserId"]) #what is the user identifier?
        if chat.chat_type == ChatType(1) or chat.chat_type == ChatType(3):
            # one on one, or mock interview: reserve chat
            chat.chat_status = 3 #reserved
        elif chat.chat_type == 2: # one on four
            num_aspiring_professionals = len(chat.aspiring_professionals)
            if num_aspiring_professionals < 4:
                # change to active
                chat.chat_status = ChatStatus(2)
            elif num_aspiring_professionals == 4:
                chat.chat_status = ChatStatus(3) # reserved
   
        session.commit()
        session.close()
 
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({
                "message": "Reserved Chat, with ID {}".format(chat_id)
                })
            }
    
    else:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in Chats table".format(chat_id)
            })
        }
