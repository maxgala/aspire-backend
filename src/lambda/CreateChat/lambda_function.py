import json
from chat import *
import inspect

import sys

sys.path.append('../../../../../')

def handler(event, context):
    session = Session()
    
    #create a new chat instance

    chat = Chat()
    chat_attribs = inspect.getmembers(Chat, lambda x: not(inspect.isroutine(x)))
    
    for attrib in chat_attribs:
        setattr(chat, attrib, event[attrib])
    
