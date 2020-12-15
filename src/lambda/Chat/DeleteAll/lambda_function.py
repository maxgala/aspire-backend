import json
import logging

from chat import Chat, ChatType, ChatStatus
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_declared_chats_frequency
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""
    senior_executive_filter = event["queryStringParameters"].get("senior_executive", "") if event["queryStringParameters"] else ""

    session = Session()
    filtered_query = session.query(Chat)
    if status_filter and status_filter in ChatStatus.__members__:
        filtered_query = filtered_query.filter(Chat.chat_status == ChatStatus[status_filter])
    if type_filter and type_filter in ChatType.__members__:
        filtered_query = filtered_query.filter(Chat.chat_type == ChatType[type_filter])
    if senior_executive_filter:
        filtered_query = filtered_query.filter(Chat.senior_executive == senior_executive_filter)

    chats = filtered_query.all()
    for chat in chats:
        admin_update_declared_chats_frequency(chat.senior_executive, -1)
        if chat.chat_status == ChatStatus.PENDING:
            admin_update_remaining_chats_frequency(chat.senior_executive, -1)
        session.delete(chat)

    session.commit()
    session.close()
    return http_status.success()
