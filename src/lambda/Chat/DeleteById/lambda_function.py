import json
import logging

from chat import Chat, ChatStatus
from base import Session
from role_validation import UserGroups, check_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_declared_chats_frequency

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'chatId'"
            })
        }

    session = Session()
    chat = session.query(Chat).get(chatId)
    if not chat:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "chat with id '{}' not found".format(chatId)
            })
        }

    admin_update_declared_chats_frequency(chat.senior_executive, -1)
    if chat.chat_status == ChatStatus.PENDING:
        admin_update_remaining_chats_frequency(chat.senior_executive, -1)

    session.delete(chat)
    session.commit()
    session.close()

    return {
        "statusCode": 200
    }
