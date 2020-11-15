import json
import logging
import boto3

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
from cognito_helpers import get_user_attributes

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        attributes = get_user_attributes(chat['senior_executive'], attributes=['given_name', 'family_name', 'custom:company'])
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
