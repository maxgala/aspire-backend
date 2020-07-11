import json
from chat import *

from base import Session
from sqlalchemy.types import DateTime
from datetime import datetime

def handler(event, context):
    info = json.loads(event["body"])
    chat_id = event["pathParameters"]["chatId"]
    
    session = Session()
    chat = session.query(Chat).get(chat_id)

    if chat != None:
        attr = "chat_status"
        curr_status = getattr(chat, attr)
        if curr_status == ChatStatus.RESERVED:
            setattr(chat, attr, ChatStatus(int(1))) #Set the chat status to pending (?) or cancelled?
            session.commit()
            session.close()

            return {
                "statusCode": 200,
                "body": json.dumps({
                "message": "Unreserved Chat, with ID {}".format(chat_id)
                })
            }
        
        else:
            session.close()
            return {
                "statusCode": 409,
                "body": json.dumps({
                "message": '''Chat with ID {} was not reserved, cannot unreserve it.
                Current chat status is {}.'''.format(chat_id, curr_status)
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
