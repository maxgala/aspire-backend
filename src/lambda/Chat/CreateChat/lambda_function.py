import json
from chat import *

from base import Session, MutableList
from sqlalchemy.types import BigInteger
from datetime import datetime

def handler(event, context):

    info = json.loads(event["body"])
    # check mandatory date for 4 on 1
    chat_type = ChatType[info["chat_type"]]
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

    launch_date = datetime(2020, 1, 1)

    for attrib in chat_attribs:
        if attrib in manual_attribs:
            if attrib == "chat_status":
                #default to pending
                setattr(chat, attrib, ChatStatus.PENDING)
            elif attrib == "date" and attrib in info:
                date = datetime.strptime(info[attrib], "%Y/%m/%d")
                setattr(chat, attrib, date)
                end_date = (date - launch_date).days ## this datetime would be the launch date
                setattr(chat,"end_date",end_date)
            elif attrib == "chat_type":
                setattr(chat, attrib, ChatType[info[attrib]])
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


    undated_chats = session.query(Chat).filter(Chat.senior_executive == info["senior_executive"])\
        .filter(Chat.date == None).filter(Chat.chat_status != "DONE") # filter by status. To accomadate for next yrs, we can get the intial date of the first chat occurence which is still active/pending. Then add those number of days onto the other chats
    fixed_chats = session.query(Chat).filter(Chat.senior_executive == info["senior_executive"])\
        .filter(Chat.date != None).filter(Chat.chat_status != "DONE")

    dates_assign = undated_chats.count() + fixed_chats.count()
    date_idx = 1 # Assuming launching on start of 2021
    space_interval = 365 // dates_assign
    for uc in undated_chats:
        fc_in_interval = False
        for fc in fixed_chats:
            fc_date = getattr(fc, "date")
            if (fc_date - launch_date).days < date_idx * space_interval and (fc_date - launch_date).days > (date_idx - 1) * space_interval: # if a fixed date chat is already in that specific time period
                fc_in_interval = True
        if fc_in_interval == True:
            date_idx += 1
        setattr(uc, "end_date", date_idx * space_interval) ##updating end_date for the existing undated chats
        date_idx += 1

    session.commit()
    session.refresh(chat)
    session.close()

    # return object as payload -- this code can be refactored
    # to be less repetetive

    chat_attribs = []
    pruned_attribs = []

    for attrib in dir(Chat):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            chat_attribs.append(attrib)

    chat_dict = {}
    for attrib in chat_attribs:
        chat_dict[attrib] = str(getattr(chat, attrib))


    return {
        "statusCode": 201,
        "body": json.dumps(chat_dict)
    }
