import json
import logging

from chat import Chat, ChatStatus
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

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return http_status.bad_request("missing path parameter(s): 'chatId'")

    session = Session()
    chat = session.query(Chat).get(chatId)
    if not chat:
        session.close()
        return http_status.not_found("chat with id '{}' not found".format(chatId))

    admin_update_declared_chats_frequency(chat.senior_executive, -1)
    if chat.chat_status == ChatStatus.PENDING:
        admin_update_remaining_chats_frequency(chat.senior_executive, -1)

    session.delete(chat)
    session.commit()
    session.close()

    return http_status.success()
