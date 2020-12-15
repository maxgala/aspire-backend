import json
import logging

from chat import Chat
from base import Session, row2dict
from role_validation import UserType, check_auth, edit_auth
from common import http_status

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

    # TODO: allow updating description, tags and fixed_date?
    # if fixed_date => what if it's active or pending with expiry_date specified?
    body = json.loads(event["body"])
    description_new = body.get('description')
    tags_new = body.get('tags')
    fixed_date_new = body.get('fixed_date')

    session.commit()
    session.refresh(chat)
    session.close()

    return http_status.success(json.dumps(row2dict(chat)))
