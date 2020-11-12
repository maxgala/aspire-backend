import json
import logging
import boto3

from chat import Chat, ChatStatus
from base import Session
from role_validation import UserGroups, check_auth, edit_auth
from cognito_helpers import admin_update_remaining_chats_frequency

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

    # CANCELED state can be achieved from PENDING, ACTIVE or RESERVED
    #
    # if chat to be canceled is dated (i.e. cannot be rescheduled):
    #   - if ACTIVE or RESERVED  => set to CANCELED
    #   - if PENDING             => N/A
    #
    # if chat to be canceled is undated (i.e. can be rescheduled):
    #   - if ACTIVE or RESERVED
    #       - set to CANCELED
    #       - create a new PENDING chat to be rescheduled
    #       - increment remaining chat frequency in Cognito
    #   - if PENDING
    #       - set to CANCELED
    #       - create a new PENDING chat to be rescheduled
    if chat.chat_status == ChatStatus.DONE or chat.chat_status == ChatStatus.CANCELED:
        session.close()
        return {
            "statusCode": 304
        }

    chat.chat_status = ChatStatus.CANCELED
    if not chat.fixed_date:
        # create new pending chat
        chat_new = Chat(
            chat_type=chat.chat_type, description=chat.description,
            chat_status=ChatStatus.PENDING, tags=chat.tags,
            senior_executive=chat.senior_executive
        )
        session.add(chat_new)

        # TODO: if has reservation(s), refund aspring professional credits and send email notification
        if chat.chat_status == ChatStatus.ACTIVE or chat.chat_status == ChatStatus.RESERVED:
            # increment remaining_chats_frequency
            # admin_update_remaining_chats_frequency(chat.senior_executive, 1)
            pass

    # TODO: send email notificatin to senior executive

    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
