import json
from chat import *
from base import Session, MutableList
import boto3

client = boto3.client('cognito-idp')

def handler(event, context):  
    # ----------------- User validation ------------------
##    try:
##        access_token = (event['headers']['Authorization']).replace('Bearer ', '')
##    except:
##        return {
##        "statusCode": 401,
##        "body": json.dumps({
##            "message": "Authorization header is expected"
##        }),
##    }
##    
##    getuserresponse = client.get_user(
##            AccessToken=access_token
##        )
##    
##    user_att = getuserresponse['UserAttributes']
##    user_id = getuserresponse['Username']
##
##    user_type = ''
##    mem_type = ''
##    credit = 0
##    
##    for att in user_att:
##        if att['Name'] == 'custom:user_type':
##            user_type = att['Value']
##        if att['Name'] == 'custom:membership_type':
##            mem_type = att['Value']
##        if att['Name'] == 'custom:credits':
##            credit = int(att['Value'])
##
##    if user_type != "Mentee":
##        return{
##            "statusCode": 409,
##            "body": json.dumps({
##            "message": "Invalid user type. Only Aspiring Professionals may reserve chats."
##            })
##        }
    # ----------------------- End user validation ------------------------------
    # user is mentee
    
    info = json.loads(event["body"])
    chat_id = event["pathParameters"]["chatId"]
    
    session = Session()
    chat = session.query(Chat).get(chat_id)
    
    if chat != None:
##        credit_cost = credit_mapping[chat.chat_type]
##        sufficient_credits = credit >= credit_cost
##        
##        if not sufficient_credits:
##            session.close()
##            return {
##                "statusCode": 409, 
##                "body": json.dumps({
##                "message": "Insufficient credits, need {} but have {}".format(credit_cost, credit)
##                })
##            }
        
        if chat.chat_status != ChatStatus.ACTIVE:
            # cannot reserve this chat, it is not active
            session.close()
            return {
                "statusCode": 409,
                "body": json.dumps({
                "message": "Chat with ID {} cannot be reserved, chat status is {}".format(chat.chat_id,
                                                                                        chat.chat_status)
                })
            }

        # ----------------------- all ok to go ahead and reserve ---------------------------
##        response = client.update_user_attributes(
##            UserAttributes=[
##                {
##                    'Name': 'custom:credits',
##                    'Value': str(int(credit) - credit_cost)
##                },
##            ],
##            AccessToken=access_token
##        )
        
        # credits updated
        if chat.aspiring_professionals == None:
            chat.aspiring_professionals = MutableList.coerce(chat.aspiring_professionals, [user_id])
            # create a new entry
        else:
             # check if user has already reserved this chat
            if user_id in chat.aspiring_professionals:
                session.close()
                return {"statusCode": 409,
                        "body": json.dumps({
                        "message": "User {} has already reserved Chat with ID {}".format(user_id, chat_id)
                        })
                    }
            else:
                #modify existing entry
                chat.aspiring_professionals.append(user_id)

        # check if chat is reserved        
        if chat.chat_type == ChatType.ONE_ON_ONE:
            # one on one, reserve chat
            chat.chat_status = ChatStatus.RESERVED #reserved
        elif chat.chat_type == ChatType.ONE_ON_FOUR: # one on four
            num_mentees = len(chat.aspiring_professionals)
            if num_mentees == 4:
                chat.chat_status = ChatStatus.RESERVED # reserved
   
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
            "message": "Reserved Chat with ID {} for User {}".format(chat_id, user_id)
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
