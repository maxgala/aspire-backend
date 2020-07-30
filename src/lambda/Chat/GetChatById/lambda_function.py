import json
from chat import *
from base import Session
from datetime import datetime

def handler(event, context):
    info = json.loads(event["body"])
    chat_id = event["pathParameters"]["chatId"]

    session = Session()
    chat = session.query(Chat).get(chat_id)
    session.close()

    chat_attribs = []
    pruned_attribs = ["chat_id"]

    for attrib in dir(Chat):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            chat_attribs.append(attrib)
    
    if chat != None:
        # construct JSON-able dictionary
        chat_dict = {}
        for attrib in chat_attribs:
            chat_dict[attrib] = str(getattr(chat, attrib)) 
            
        return {"statusCode": 200,
                "body": json.dumps(chat_dict)
        }
        
    
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in Chats table".format(chat_id)
            })
        }
