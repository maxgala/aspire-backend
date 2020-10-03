# import pandas as pd
# import numpy as np
import csv
import datetime
import json
from chat import *

from base import Session, MutableList
from sqlalchemy.types import BigInteger, Boolean
FILEPATH = './sample/data.csv'
def renameColumns(data):
    return data.rename(columns={
        'Frequency': 'frequency',
        'date': 'fixed_dates',
        'senior_executive': 'email'
    }, inplace=True)
# def cleanData(data):
#     return data.replace(np.nan, "", inplace=True)
def loadData(session):
    with open(FILEPATH, 'r') as csv_file:
        data = csv.DictReader(csv_file, delimiter=',')
        #renameColumns(data)
        # cleanData(data)
        # create new data
        new_data = []
        for row in data:
            fixed_dates = list(filter(lambda date: len(date) > 0,
                                      row['date'].split(",")))
            num_dates_autoassign = int(row['Frequency']) - len(fixed_dates)
            if num_dates_autoassign < 0:
                raise ValueError("Invalid data in row ", row)
            chat_index = 0
            # place fixed dates first
            for date in fixed_dates:
                new_data.append({
                    'id': row['senior_executive'] + str(chat_index),
                    'senior_executive': row['senior_executive'],
                    'type': row['chat_type'],
                    'description': row['description'],
                    'tags' : row['tags'].split(","),
                    #'credits' : row['credits'], ### Hard coded it rn, has to be changed depending on the chat_type
                    'end_date': (datetime.strptime(date, '%Y/%m/%d') - datetime(2020, 1, 1)).days, 
                    'date': datetime.strptime(date, '%Y/%m/%d') ## For fixed date, date and end_date are same
                })
                chat_index += 1
            # assign dates spaced out 365/num_dates_autoassign
            date_idx = 1 # Assuming launching on start of 2021
            space_interval = 365 // num_dates_autoassign
            while date_idx < num_dates_autoassign + 1:
                new_data.append({
                    'id': row['senior_executive'] + str(chat_index),
                    'senior_executive': row['senior_executive'],
                    'type': row['chat_type'],
                    'end_date': date_idx * space_interval,
                    'tags' : row['tags'].split(","),
                    'description': row['description'],
                    #'credits' : row['credits'], ### Hard coded it rn, has to be changed depending on the chat_type
                })
                chat_index += 1
                date_idx += 1

    for x in new_data:
        if x['type'] == '1on1':
            x['type'] = 'ONE_ON_ONE'
            x['credits'] = 5
        if 'date' in x:
            row = Chat(chat_type = ChatType[x['type']],senior_executive = x['senior_executive'],\
                 end_date = x['end_date'], chat_status = ChatStatus.PENDING, date = x['date'], \
                     credits = x['credits'], description = x['description'], tags = x['tags'])
        else:
            row = Chat(chat_type = ChatType[x['type']],senior_executive = x['senior_executive'],\
                 end_date = x['end_date'], chat_status = ChatStatus.PENDING, credits = x['credits'],\
                     description = x['description'], tags = x['tags'])            
        session.add(row)
    #print(new_data)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    #session.execute('''TRUNCATE TABLE scheduler''')
    loadData(session)
    session.commit()
    session.close()