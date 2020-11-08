import json
import logging
import boto3

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserGroups, check_auth

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def edit_credits(user, access_token, value):
    user_credits = user.get('custom:credits')
    response = client.update_user_attributes(
        UserAttributes=[
            {
                'Name': 'custom:credits',
                'Value': str(int(user_credits) + value)
            },
        ],
        AccessToken=access_token
    )
    logger.info(response)

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.PAID
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_groups)
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

    # to unreserve, chat must be either ACTIVE(multi aspiring professional chats) or RESERVED(single aspiring professional chats)
    # in addition, user must have reserved this chat
    #
    # if chat_status is RESERVED => set to ACTIVE
    if chat.chat_status != ChatStatus.ACTIVE and chat.chat_status != ChatStatus.RESERVED:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "cannot unreserve inactive or unreserved chat with id '{}'".format(chatId)
            })
        }
    if not chat.aspiring_professionals or user['email'] not in chat.aspiring_professionals:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' did not reserve chat with id '{}'".format(user['email'], chatId)
            })
        }

    # TODO: find a better way to pop from list
    aspiring_professionals = chat.aspiring_professionals
    chat.aspiring_professionals = None
    for ap in aspiring_professionals:
        if ap != user['email']:
            if chat.aspiring_professionals:
                chat.aspiring_professionals.append(ap)
            else:
                chat.aspiring_professionals = [ap]

    # edit_credits(user, access_token, credit_mapping[chat.chat_type])
    if chat.chat_status == ChatStatus.RESERVED:
        chat.chat_status = ChatStatus.ACTIVE

    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
