import json
import logging
import boto3

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
from role_validation import UserGroups

client = boto3.client('cognito-idp')
userPoolId = 'us-east-1_T02rYkaXy'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_user_attributes(email, attributes=['given_name', 'family_name', 'custom:company']):
    response = client.list_users(
        UserPoolId=userPoolId,
        AttributesToGet=attributes,
        Filter = 'email="{}"'.format(email)
    )
    logger.info(response)

    raw_attributes = response['Users'][0]['Attributes']
    attributes = {}
    for attr in raw_attributes:
        attributes[attr['Name']] = attr['Value']
    return attributes

def handler(event, context):
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
        attributes = get_user_attributes(chat['senior_executive'])
        chat['given_name'] = attributes['given_name']
        chat['family_name'] = attributes['family_name']
        chat['custom:company'] = attributes['custom:company']

    return {
        "statusCode": 200,
        "body": json.dumps({
            "chats": chats_modified,
            "count": len(chats_modified)
        })
    }
