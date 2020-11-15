import json
import logging

from chat import Chat
from base import Session, row2dict
from role_validation import UserGroups, check_auth, edit_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_groups)
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
    success = edit_auth(user, chat.senior_executive)
    if not success:
        # caller does not own the resource
        session.close()
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    # TODO: allow updating description, tags and fixed_date?
    # if fixed_date => what if it's active or pending with expiry_date specified?
    body = json.loads(event["body"])
    description_new = body.get('description')
    tags_new = body.get('tags')
    fixed_date_new = body.get('fixed_date')

    session.commit()
    session.refresh(chat)
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(chat)
        )
    }
