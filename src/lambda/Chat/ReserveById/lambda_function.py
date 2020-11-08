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

    # RESERVED state can be achieved from ACTIVE state only (must have sufficient funds)
    # if chat_type is ONE_ON_ONE or MOCK_INTERVIEW, mark as reserved:
    ## append aspiring_professional, set to RESERVED
    # if chat_type is FOUR_ON_ONE:
    ## append aspiring_professional, set to RESERVED (if all four booked)
    if chat.chat_status != ChatStatus.ACTIVE:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "cannot reserve inactive chat with id '{}'".format(chatId)
            })
        }
    if chat.aspiring_professionals and user['email'] in chat.aspiring_professionals:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' already reserved chat with id '{}'".format(user['email'], chatId)
            })
        }

    # if int(user['custom:credits']) < credit_mapping[chat.chat_type]:
    #     session.close()
    #     return {
    #         "statusCode": 403,
    #         "body": json.dumps({
    #             "errorMessage": "user '{}' does not have sufficient credits to reserve chat with id '{}'".format(user['email'], chatId)
    #         })
    #     }
    # edit_credits(user, access_token, (-credit_mapping[chat.chat_type]))

    if chat.chat_type == ChatType.FOUR_ON_ONE:
        if chat.aspiring_professionals:
            chat.aspiring_professionals.append(user['email'])
        else:
            chat.aspiring_professionals = [user['email']]

        if len(chat.aspiring_professionals) == 4:
            chat.chat_status = ChatStatus.RESERVED
    else:
        chat.chat_status = ChatStatus.RESERVED
        chat.aspiring_professionals = [user['email']]

    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
