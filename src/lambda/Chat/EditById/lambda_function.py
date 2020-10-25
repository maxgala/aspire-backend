import json
import logging

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
# from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_groups = [
    #     UserGroups.ADMIN,
    #     UserGroups.MENTOR
    # ]
    # err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    # if err:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": group_response
    #         })
    #     }

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
    # - chat_status, description, tags
    # - date, end_date
    # - aspiring_professionals

    session.commit()
    session.refresh(chat)
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(chat)
        )
    }
