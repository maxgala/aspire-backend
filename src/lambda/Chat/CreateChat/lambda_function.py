import json
from chat import *

from base import Session, MutableList
from sqlalchemy.types import BigInteger
from datetime import datetime

def handler(event, context):
    
    info = json.loads(event["body"])
    # check mandatory date for 4 on 1
    chat_type = ChatType(int(info["chat_type"]))
    if chat_type in mandatory_date:
        if "date" not in info:
            return {"statusCode": 400,\
                    "body": json.dumps({
                    "message": "For a {} chat, date must be specified".format(chat_type)
                    })
            }
    # ------------------- passed date check ----------------------------

    
    session = Session()
    #create a new chat instance

    chat = Chat()
    chat_attribs = dir(Chat)

    manual_attribs = ["chat_id", "credits", "created_on", "updated_on", \
                      "chat_status", "chat_type", "date",\
                      "aspiring_professionals"]
    # ignore primary key, dates automatically set
    

    for attrib in chat_attribs:
        if attrib in manual_attribs:
            if attrib == "chat_status":
                #default to pending
                setattr(chat, attrib, ChatStatus.PENDING)
            elif attrib == "date" and attrib in info:
                setattr(chat, attrib, BigInteger(info[attrib]))
            elif attrib == "chat_type":
                setattr(chat, attrib, ChatType(int(info[attrib])))
            elif attrib == "aspiring_professionals":
                chat.aspiring_professionals = MutableList.coerce("chat.aspiring_professionals", info[attrib])
                # else skip, it it handled automatically by sqlalchemy
        elif not (attrib.startswith('_') or attrib.strip() == "metadata"):
            try:
                setattr(chat, attrib, info[attrib])
            except: # in case underspecified?
                continue

    # do this at the end to avoid any errors with chat_type being set
    setattr(chat, "credits", credit_mapping[chat.chat_type])


    
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
