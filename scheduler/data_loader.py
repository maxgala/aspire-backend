import pandas as pd
import numpy as np
import datetime

FILEPATH = './sample/data.csv'


def renameColumns(data):
    return data.rename(columns={
        'Frequency': 'frequency',
        'date': 'fixed_dates',
        'senior_executive': 'email'
    }, inplace=True)


def cleanData(data):
    return data.replace(np.nan, "", inplace=True)


def loadData():
    data = pd.read_csv(FILEPATH)

    renameColumns(data)
    cleanData(data)

    # create new data
    new_data = []

    for index, row in data.iterrows():
        fixed_dates = list(filter(lambda date: len(date) > 0,
                                  row['fixed_dates'].split(",")))
        num_dates_autoassign = row['frequency'] - len(fixed_dates)

        if num_dates_autoassign < 0:
            raise ValueError("Invalid data in row ", row)

        chat_index = 0

        # place fixed dates first
        for date in fixed_dates:
            new_data.append({
                'id': row['email'] + str(chat_index),
                'email': row['email'],
                'type': row['chat_type'],
                'end_date': (datetime.datetime.strptime(date, '%Y/%m/%d') - datetime.datetime(2020, 1, 1)).days,
                'booked': False,
            })
            chat_index += 1

        # assign dates spaced out 365/num_dates_autoassign
        date_idx = 0
        space_interval = 365 // num_dates_autoassign
        while date_idx < num_dates_autoassign:
            new_data.append({
                'id': row['email'] + str(chat_index),
                'email': row['email'],
                'type': row['chat_type'],
                'end_date': date_idx * space_interval,
                'booked': False,
            })
            chat_index += 1
            date_idx += 1

    print(new_data)


loadData()
