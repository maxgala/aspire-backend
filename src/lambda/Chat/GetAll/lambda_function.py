import json
import logging

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
from role_validation import UserGroups, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # validate authorization
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

    # TODO: return user info? add SE's first and last names and company
    return {
        "statusCode": 200,
        "body": json.dumps({
            "chats": [row2dict(r) for r in chats],
            "count": len(chats)
        })
    }
