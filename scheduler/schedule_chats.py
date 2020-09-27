'''
Simplified scheduler logic.
Immediately selects chats that expire in the next 21 days.
Additionally, chooses 15 coffee chats (including ones chosen because they expire in the next 21 days).
No integration with BE yet.
'''

# from data_loader import loadData
import random
import json
import datetime
from chat import Chat
from base import Session, MutableList,row2dict

CHATS_TO_CHOOSE = 15


def sortByExpiryDate(data):
    return sorted(data, key=lambda row: row['end_date'], reverse=False)


def removeExpiredChats(data, current_day):
    return list(filter(lambda row: row['end_date'] > current_day and row['chat_status'] != 'RESERVED' and row['chat_status'] != 'DONE', data)) #add the status check

def schedule(data):
    current_day = (datetime.datetime(2020,1,25) -
                   datetime.datetime(2020, 1, 1)).days
    #print(current_day)
    data = sortByExpiryDate(data)
    data = removeExpiredChats(data, current_day)

    selected_chats = []

    remaining_chats = []
    # choose chats occuring in the new 21 days
    for row in data:
        if row['end_date'] - current_day <= 21:
            selected_chats.append(row)
        elif row['date'] == None: # to select the chats which didnt have a fixed date (i.e. date field was Null)
            remaining_chats.append(row)
    #print(len(selected_chats))
    #print(len(remaining_chats))
    # randomly sample from the remaining array and add
    # to selected chats
    # note: dummy logic - can be "smarter" in the future
    remaining = CHATS_TO_CHOOSE - len(selected_chats)
    upcoming_chats = remaining_chats[:50]
    while remaining > 0 and len(upcoming_chats) > 0:
        r = random.randint(0, len(upcoming_chats) - 1)
        chosen = upcoming_chats.pop(r)
        selected_chats.append(chosen)
        ##### change the status of the chat to active 
        remaining -= 1

    return selected_chats

# example input
# a full read from the database serialized as json will suffice
# print(schedule(loadData()))
def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    chats = session.query(Chat).all()
    chatslist = []
    for chat in chats:
        chatdict = row2dict(chat)
        chatslist.append(chatdict)
    scheduled_chats = schedule(chatslist)
    session.close()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "chats": scheduled_chats,
            "count": len(scheduled_chats)
        })
    }
