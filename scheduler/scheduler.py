'''
Simplified scheduler logic.
Immediately selects chats that expire in the next 21 days.
Additionally, chooses 15 coffee chats (including ones chosen because they expire in the next 21 days).
No integration with BE yet.
'''

# from data_loader import loadData
import datetime
import random

CHATS_TO_CHOOSE = 15


def sortByExpiryDate(data):
    return sorted(data, key=lambda row: row['end_date'], reverse=False)


def removeExpiredChats(data, current_day):
    return list(filter(lambda row: row['end_date'] > current_day, data))


def schedule(data):
    current_day = (datetime.datetime.today() -
                   datetime.datetime(2020, 1, 1)).days
    data = sortByExpiryDate(data)
    data = removeExpiredChats(data, current_day)

    selected_chats = []

    remaining_chats = []
    # choose chats occuring in the new 21 days
    for row in data:
        if row['end_date'] - current_day <= 0:
            selected_chats.append(row)
        else:
            remaining_chats.append(row)

    # randomly sample from the remaining array and add
    # to selected chats
    # note: dummy logic - can be "smarter" in the future
    remaining = CHATS_TO_CHOOSE - len(selected_chats)

    while remaining > 0 and len(remaining_chats) > 0:
        r = random.randint(0, len(remaining_chats) - 1)
        chosen = remaining_chats.pop(r)
        selected_chats.append(chosen)

    return selected_chats

# example input
# a full read from the database serialized as json will suffice
# print(schedule(loadData()))
