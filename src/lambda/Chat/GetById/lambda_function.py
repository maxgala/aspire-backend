import json
import logging

from chat import Chat
from base import Session, row2dict
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return http_status.bad_request("missing path parameter(s): 'chatId'")

    session = Session()
    chat = session.query(Chat).get(chatId)
    session.close()
    if not chat:
        return http_status.not_found("chat with id '{}' not found".format(chatId))

    return http_status.success(json.dumps(
            row2dict(chat)
        ))