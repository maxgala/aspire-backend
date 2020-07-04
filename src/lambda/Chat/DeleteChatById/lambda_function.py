import json
from chat import *
from base import Session
from datetime import datetime

def handler(event, context):
    info = json.loads(event["body"])
    chat_id = event["pathParameters"]["chat_id"]

    session = Session()
    chat = session.query(Chat).get(chat_id)

    if chat != None:
        session.delete(chat)
        session.commit()
        session.close()
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Chat Row with ID {} deleted".format(chat_id)
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
