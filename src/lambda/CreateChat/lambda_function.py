import json
from chat import *
import inspect
from base import Session, engine, Base

def handler(event, context):
    session = Session()
    
    #create a new chat instance
    chat = Chat()
    chat_attribs = dir(Chat)
    
    for attrib in chat_attribs:
        if not (attrib.startswith('_') or attrib.strip() == "metadata"):
            #print(attrib)
            setattr(chat, attrib, event[attrib])
