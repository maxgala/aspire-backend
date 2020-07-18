import json
from chat import *

from base import Session
from sqlalchemy.types import DateTime
from datetime import datetime

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
    user_id = getuserresponse['Username']

    user_type = ''
    mem_type = ''
    credit = 0
    
    for att in user_att:
        if att['Name'] == 'custom:user_type':
            user_type = att['Value']
        if att['Name'] == 'custom:membership_type':
            mem_type = att['Value']
        if att['Name'] == 'custom:credits':
            credit = int(att['Value'])

    if user_type != "Mentee":
        return{
            "statusCode": 409,
            "body": json.dumps({
            "message": "Invalid user type. Only Aspiring Professionals may reserve chats."
            })
        }
    # ----------------------- End user validation ------------------------------
    
    info = json.loads(event["body"])
    chat_id = event["pathParameters"]["chatId"]
    
    session = Session()
    chat = session.query(Chat).get(chat_id)

    if chat != None:
        # do we refund the credits? 
        # check if user is in the list
        if user_id in chat.aspiring_professionals:
            # k let's get you off this list
            # get the index
            i = chat.aspiring_professionals.index(user_id)
            #pop the user
            chat.aspiring_professionals.pop(i)
            #all done!
            session.close()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "User {} has un-reserved Chat with ID {}".format(user_id, chat_id)
                })
            }            
        else:
            session.close() # didn't even reserve this chat yet my dude
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "User {} has not reserved Chat with ID {}, cannot un-reserve".format(user_id, chat_id)
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
