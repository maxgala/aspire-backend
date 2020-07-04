import json
from chat import *
from base import Session
from datetime import datetime

def handler(event, context):
    session = Session()
    chats = session.query(Chat).all()
    session.close()

    chat_attribs = []
    pruned_attribs = [] # can set attribs to skip, empty list for now

    for attrib in dir(Chat):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            chat_attribs.append(attrib)

    chats_list = [None] * len(chats) # preallocate in case table is large
    
    for i in range(len(chats)):
        chat_dict = {}
        for attrib in chat_attribs:
            chat_dict[attrib] = str(getattr(chats[i], attrib))
            
        chats_list[i] = chat_dict
            
    return {"statusCode": 200,
            "body": json.dumps(chats_list)
    }
