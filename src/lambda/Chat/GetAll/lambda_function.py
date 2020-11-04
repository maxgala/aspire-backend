import json
import logging
import boto3

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
from role_validation import UserGroups, check_auth

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID,
        UserGroups.FREE
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""
    senior_executive_filter = event["queryStringParameters"].get("senior_executive", "") if event["queryStringParameters"] else ""

    session = Session()
    # TODO: more filters? (tags)
    filtered_query = session.query(Chat)
    if status_filter and status_filter in ChatStatus.__members__:
        filtered_query = filtered_query.filter(Chat.chat_status == ChatStatus[status_filter])
    if type_filter and type_filter in ChatType.__members__:
        filtered_query = filtered_query.filter(Chat.chat_type == ChatType[type_filter])
    if senior_executive_filter:
        filtered_query = filtered_query.filter(Chat.senior_executive == senior_executive_filter)

    chats = filtered_query.all()
    session.close()

    chats_modified = [row2dict(r) for r in chats]
    for chat in chats_modified:
        response = client.list_users(
            UserPoolId='us-east-1_T02rYkaXy',
            AttributesToGet=[
                'given_name','family_name','custom:company'
            ],
            Filter = 'email="{}"'.format(chat["senior_executive"])
        )
        attributes = response['Users'][0]['Attributes']
        for attr in attributes:
            if attr['Name'] == 'given_name':
                chat['given_name'] = attr['Value']
            elif attr['Name'] == 'family_name':
                chat['family_name'] = attr['Value']
            elif attr['Name'] == 'custom:company':
                chat['custom:company'] = attr['Value']

    return {
        "statusCode": 200,
        "body": json.dumps({
            "chats": chats_modified,
            "count": len(chats_modified)
        })
    }
