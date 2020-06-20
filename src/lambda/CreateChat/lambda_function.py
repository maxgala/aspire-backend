import json
from chat import *
import inspect
from base import Session, engine, Base

def handler(event, context):
    session = Session()
    
    #create a new chat instance
    chat = Chat()
    chat_attribs = dir(Chat)

    info = json.loads(event["body"])
    for attrib in chat_attribs:
        if not (attrib.startswith('_') or attrib.strip() == "metadata"):
            #print(attrib)
            setattr(chat, attrib, info[attrib])
            # does not take into account the enums


























    session.add(chat)
    session.commit()
    session.close()
