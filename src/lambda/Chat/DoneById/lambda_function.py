import json
import logging

from chat import Chat, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth, edit_auth
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
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

    success = edit_auth(user, chat.senior_executive)
    if not success:
        session.close()
        return http_status.unauthorized()
 
    # DONE state can be achieved from RESERVED_CONFIRMED
    if chat.chat_status != ChatStatus.RESERVED_CONFIRMED:
        session.close()
        return http_status.forbidden("cannot mark DONE unconfirmed reservation of chat with id '{}'".format(chatId))

    chat.chat_status = ChatStatus.DONE

    session.commit()
    session.close()
    return http_status.success()
