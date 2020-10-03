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
        attrs_to_update = info.keys()
        for attr in attrs_to_update:
            if attr == "chat_status":
                setattr(chat, attr, ChatStatus(eval(ChatStatus.__name__ + '.' + info[attr])))
            elif attr == "chat_type":
                setattr(chat, attr, ChatType(eval(ChatType.__name__ + '.' + info[attr])))
            else:
                setattr(chat, attr, info[attr])
            
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
            "message": "Updated Chat Row, with ID {}".format(chat_id)
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
