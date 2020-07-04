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
                setattr(chat, attrib, ChatStatus(int(info[attrib])))
            elif attrib == "chat_type":
                setattr(chat, attrib, ChatType(int(info[attrib])))
            # else skip, it it handled automatically by sqlalchemy
        elif not (attrib.startswith('_') or attrib.strip() == "metadata"):
            try:
                attrib_data =  info[attrib]
                setattr(chat, attrib, attrib_data)
            except:
                continue
                
    session.add(chat)
    session.commit()
    
    session.refresh(chat)
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Created Chat Row, with ID {}".format(chat.chat_id)
        }),
    }
