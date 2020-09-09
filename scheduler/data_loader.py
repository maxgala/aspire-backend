# import pandas as pd
# import numpy as np
import csv
import datetime
import json
from scheduler import *

from base import Session, MutableList
from sqlalchemy.types import BigInteger
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
                    'email': row['senior_executive'],
                    'type': row['chat_type'],
                    'end_date': (datetime.strptime(date, '%Y/%m/%d') - datetime(2020, 1, 1)).days,
                    'booked': False,
                })
                chat_index += 1
            # assign dates spaced out 365/num_dates_autoassign
            date_idx = 0
            space_interval = 365 // num_dates_autoassign
            while date_idx < num_dates_autoassign:
                new_data.append({
                    'id': row['senior_executive'] + str(chat_index),
                    'email': row['senior_executive'],
                    'type': row['chat_type'],
                    'end_date': date_idx * space_interval,
                    'booked': False,
                })
                chat_index += 1
                date_idx += 1

    for x in new_data:
        if x['type'] == '1on1':
            x['type'] = 'ONE_ON_ONE'
        row = Scheduler(chat_type = ChatType[x['type']],email = x['email'],end_date = x['end_date'], chat_status = ChatStatus.ACTIVE)
        session.add(row)
    print(new_data)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    session.execute('''TRUNCATE TABLE scheduler''')
    loadData(session)
    session.commit()
    session.close()