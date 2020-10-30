import json
import logging
import boto3

from chat import Chat, ChatStatus, credit_mapping
from base import Session
from role_validation import UserGroups, read_auth, edit_auth

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def edit_chats_frequency(user, access_token, value):
    user_chats_frequency = user.get('custom:chats_frequency')
    response = client.update_user_attributes(
        UserAttributes=[
            {
                'Name': 'custom:chats_frequency',
                'Value': str(int(user_chats_frequency) + value)
            },
        ],
        AccessToken=access_token
    )
    logger.info(response)

def handler(event, context):
    # validate authorization
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
    ## if RESERVED          => set to CANCELED
    ## if PENDING or ACTIVE => set to CANCELED and decrement remaining chat frequency in Cognito
    #
    # if chat to be canceled is undated (i.e. can be rescheduled):
    ## if RESERVED          => set to CANCELED and create a new PENDING chat to be rescheduled
    ##                         and increment remaining chat frequency in Cognito
    ## if PENDING or ACTIVE => set to CANCELED and create a new PENDING chat to be rescheduled
    if chat.chat_status == ChatStatus.DONE or chat.chat_status == ChatStatus.CANCLED:
        return {
            "statusCode": 304
        }

    chat.chat_status == ChatStatus.CANCELED
    if chat.chat_status == ChatStatus.RESERVED and not chat.date:
        # increment chats_frequency
        edit_chats_frequency(user, access_token, 1)

        # create new pending chat
        chat_new = Chat(
            chat_type=chat.chat_type, description=chat.description,
            credits=credit_mapping[chat.chat_type], chat_status=ChatStatus.PENDING,
            senior_executive=chat.senior_executive, tags=chat.tags
        )
        session.add(chat_new)
    elif chat.chat_status != ChatStatus.RESERVED:
        # PENDING or ACTIVE
        if chat.date:
            # decrement chats_frequency
            edit_chats_frequency(user, access_token, -1)
        else:
            # create new pending chat
            chat_new = Chat(
                chat_type=chat.chat_type, description=chat.description,
                credits=credit_mapping[chat.chat_type], chat_status=ChatStatus.PENDING,
                senior_executive=chat.senior_executive, tags=chat.tags
            )
            session.add(chat_new)

    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
