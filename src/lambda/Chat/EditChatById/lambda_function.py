import json
from chat import *

from base import Session
from sqlalchemy.types import DateTime
from datetime import datetime

def handler(event, context):
    info = json.loads(event["body"])
    chat_id = info["chat_id"]
    
    session = Session()
    chat = session.query(Chat).get(chat_id)

    if chat != None:
        attrs_to_update = info.keys()
        for attr in attrs_to_update:
            setattr(chat, attr, info[attr])
            
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
            "message": "Updated Chat Row, with ID {}".format(chat.chat_id)
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
