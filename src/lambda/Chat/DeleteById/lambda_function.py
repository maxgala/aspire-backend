import json
import logging

from chat import Chat
from base import Session
from role_validation import UserGroups, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # validate authorization
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

    session.delete(chat)
    session.commit()
    session.close()

    return {
        "statusCode": 200
    }
