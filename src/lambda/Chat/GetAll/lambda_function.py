import json
import logging

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
from cognito_helpers import get_users

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""
    user_filter = event["queryStringParameters"].get("email", "") if event["queryStringParameters"] else ""

    session = Session()
    # TODO: more filters? (tags)
    filtered_query = session.query(Chat)
    if status_filter and status_filter in ChatStatus.__members__:
        filtered_query = filtered_query.filter(Chat.chat_status == ChatStatus[status_filter])
    if type_filter and type_filter in ChatType.__members__:
        filtered_query = filtered_query.filter(Chat.chat_type == ChatType[type_filter])
    if user_filter:
        user, _ = get_users(filter_=('email', user_filter), attributes_filter=['custom:user_type'])
        user_type = user['attributes']['custom:user_type']
        if user_type == 'PAID' or user_type == 'FREE':
            filtered_query = filtered_query.filter(Chat.aspiring_professionals.any(user_filter))
        elif user_type == 'MENTOR':
            filtered_query = filtered_query.filter(Chat.senior_executive == user_filter)

    chats = filtered_query.all()
    session.close()

    # attrs = ['email', 'given_name', 'family_name', 'picture', 'custom:user_type', 'custom:user_type']
    users, _ = get_users()
    chats_modified = [row2dict(r) for r in chats]
    for chat in chats_modified:
        for user in users:
            if chat['senior_executive'] == user['attributes']['email']:
                chat['given_name'] = user['attributes']['given_name']
                chat['family_name'] = user['attributes']['family_name']
                chat['picture'] = user['attributes']['picture']
                chat['custom:company'] = user['attributes']['custom:company']
                break

    return {
        "statusCode": 200,
        "body": json.dumps({
            "chats": chats_modified,
            "count": len(chats_modified)
        }),
        "headers": {
            'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
        }
    }
