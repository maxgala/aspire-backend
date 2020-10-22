import json
from chat import *
from base import Session
from datetime import datetime
import boto3
client = boto3.client('cognito-idp')

def handler(event, context):
    session = Session()
    chats = session.query(Chat).all()
    session.close()

    chat_attribs = []
    pruned_attribs = [] # can set attribs to skip, empty list for now

    for attrib in dir(Chat):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            chat_attribs.append(attrib)

    chats_list = [None] * len(chats) # preallocate in case table is large

    for i in range(len(chats)):
        chat_dict = {}
        for attrib in chat_attribs:
            chat_dict[attrib] = str(getattr(chats[i], attrib))
        response = client.list_users(
            UserPoolId='us-east-1_T02rYkaXy',
            AttributesToGet=[
                'given_name','family_name','custom:company'
            ],
            Filter = 'email="{}"'.format(chats[i].senior_executive)
        )
        atts = response['Users'][0]['Attributes']
        for att in atts:
            if att['Name'] == 'given_name':
                chat_dict['given_name'] = att['Value']
            elif att['Name'] == 'family_name':
                chat_dict['family_name'] = att['Value']
            elif att['Name'] == 'custom:company':
                chat_dict['custom:company'] = att['Value']

        chats_list[i] = chat_dict

    chats_dict = {}
    chats_dict["chats"] = chats_list
    chats_dict["count"] = len(chats_list)
    return {"statusCode": 200,
            "body": json.dumps(chats_dict)
    }
