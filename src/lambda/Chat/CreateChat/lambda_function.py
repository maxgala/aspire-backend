import json
from chat import *

from base import Session

from datetime import datetime

def handler(event, context):
    session = Session()
    
    #create a new chat instance
    chat = Chat()
    chat_attribs = dir(Chat)

    manual_attribs = ["chat_id", "date", "created_on", "updated_on", \
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
            setattr(chat, attrib, info[attrib])

    session.add(chat)
    session.commit()
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Created Chat Row"
        }),
    }
