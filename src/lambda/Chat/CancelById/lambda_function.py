import json
import logging
import boto3

from chat import Chat, ChatStatus, credit_mapping
from base import Session
from role_validation import UserGroups, read_auth, edit_auth

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def edit_remaining_chats_frequency(user, access_token, value):
    remaining_chats_frequency = user.get('custom:remaining_chats_frequency')
    response = client.update_user_attributes(
        UserAttributes=[
            {
                'Name': 'custom:remaining_chats_frequency',
                'Value': str(int(remaining_chats_frequency) + value)
            },
        ],
        AccessToken=access_token
    )
    logger.info(response)

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR
    ]
    success, user = read_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }
    access_token = event['headers']['X-Aspire-Access-Token']
    if not access_token:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "access token header required"
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

    # CANCELED state can be achieved from PENDING, ACTIVE or RESERVED
    #
    # if chat to be canceled is dated (i.e. cannot be rescheduled):
    #   - if ACTIVE or RESERVED  => set to CANCELED
    #   - if PENDING             => set to CANCELED and decrement remaining chat frequency in Cognito
    #
    # if chat to be canceled is undated (i.e. can be rescheduled):
    #   - if ACTIVE or RESERVED
    #       - set to CANCELED
    #       - create a new PENDING chat to be rescheduled
    #       - increment remaining chat frequency in Cognito
    #   - if PENDING
    #       - set to CANCELED
    #       - create a new PENDING chat to be rescheduled
    if chat.chat_status == ChatStatus.DONE or chat.chat_status == ChatStatus.CANCLED:
        return {
            "statusCode": 304
        }

    chat.chat_status == ChatStatus.CANCELED
    if chat.chat_status == ChatStatus.ACTIVE or chat.chat_status == ChatStatus.RESERVED:
        if not chat.fixed_date:
            # increment remaining_chats_frequency
            edit_remaining_chats_frequency(user, access_token, 1)

            # create new pending chat
            chat_new = Chat(
                chat_type=chat.chat_type, description=chat.description,
                chat_status=ChatStatus.PENDING, tags=chat.tags,
                senior_executive=chat.senior_executive
            )
            session.add(chat_new)
    if chat.chat_status == ChatStatus.PENDING:
        if chat.fixed_date:
            # decrement remaining_chats_frequency
            edit_remaining_chats_frequency(user, access_token, -1)
        else:
            # create new pending chat
            chat_new = Chat(
                chat_type=chat.chat_type, description=chat.description,
                chat_status=ChatStatus.PENDING, tags=chat.tags,
                senior_executive=chat.senior_executive
            )
            session.add(chat_new)

    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
