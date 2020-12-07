import json
import logging

from chat import Chat, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_credits

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
        session.close()
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    # CANCELED state can be achieved from PENDING, ACTIVE, RESERVED_PARTIAL, RESERVED or RESERVED_CONFIRMED
    #
    # if chat to be canceled is dated (i.e. cannot be rescheduled):
    #   - if PENDING    => N/A
    #   - else          => set to CANCELED, refund APs
    #
    # if chat to be canceled is undated (i.e. can be rescheduled):
    #   - set to CANCELED
    #   - refund APs
    #   - create a new PENDING chat to be rescheduled
    #   - if not PENDING
    #       - increment remaining chat frequency in Cognito
    # TODO: send email notification to SEs and APs
    if chat.chat_status == ChatStatus.DONE or chat.chat_status == ChatStatus.CANCELED or chat.chat_status == ChatStatus.EXPIRED:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "cannot cancel DONE, CANCELED or EXPIRED chat with id '{}'".format(chatId)
            })
        }

    for ap in chat.aspiring_professionals:
        admin_update_credits(ap, credit_mapping[chat.chat_type])

    if not chat.fixed_date:
        chat_new = Chat(
            chat_type=chat.chat_type, description=chat.description,
            chat_status=ChatStatus.PENDING, tags=chat.tags,
            senior_executive=chat.senior_executive
        )
        session.add(chat_new)

        if chat.chat_status != ChatStatus.PENDING:
            admin_update_remaining_chats_frequency(chat.senior_executive, 1)
    chat.chat_status = ChatStatus.CANCELED

    session.commit()
    session.close()
    return {
        "statusCode": 200
    }
