import json
import logging

from chat import Chat, ChatType, ChatStatus
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
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    body = json.loads(event["body"])
    chat_status_new = body.get('chat_status')
    if chat_status_new and chat_status_new not in ChatStatus.__members__:
        session.close()
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'chat_status'"
            })
        }

    # TODO: attributes that can be updated:
    # - description, tags
    # - fixed_date, expiry_date

    # chat_status:
    ## PENDING => ACTIVE, CANCELED
    ## ACTIVE => PENDING, RESERVED, CANCLED
    ## RESERVED => ACTIVE, DONE, CANCLED

    session.commit()
    session.refresh(chat)
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(chat)
        )
    }
