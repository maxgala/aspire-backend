import json
from chat import *

from base import Session
from sqlalchemy.types import DateTime
from datetime import datetime

def handler(event, context):
    session = Session()
    
    #create a new chat instance
    chat = Chat()
    chat_attribs = dir(Chat)

    manual_attribs = ["chat_id", "created_on", "updated_on", \
                      "chat_status", "chat_type"]
    # ignore primary key, dates automatically set
    
    info = json.loads(event["body"])
    
    for attrib in chat_attribs:
        if attrib in manual_attribs:
            if attrib == "chat_status":
                #setattr(chat, attrib, ChatStatus(int(info[attrib])))
                #default to pending
                setattr(chat, attrib, ChatStatus(1))
            elif attrib == "chat_type":
                setattr(chat, attrib, ChatType(int(info[attrib])))
            # else skip, it it handled automatically by sqlalchemy
        elif not (attrib.startswith('_') or attrib.strip() == "metadata"):
            try:
                setattr(chat, attrib, info[attrib])
            except: # in case underspecified?
                continue
                
    session.add(chat)
    session.commit()
    session.refresh(chat)
    session.close()

    # return object as payload -- this code can be refactored
    # to be less repetetive
    
    chat_attribs = []
    pruned_attribs = ["chat_id"]

    for attrib in dir(Chat):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            chat_attribs.append(attrib)
            
    chat_dict = {}
    for attrib in chat_attribs:
        chat_dict[attrib] = str(getattr(chat, attrib)) 

    return {
        "statusCode": 200,
        "body": json.dumps(chat_dict)
    }
