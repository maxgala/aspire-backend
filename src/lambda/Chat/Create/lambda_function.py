import json
import logging
import boto3
from datetime import datetime

from chat import Chat, ChatType, ChatStatus, credit_mapping, mandatory_date
from base import Session
from role_validation import UserGroups, check_auth

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

    # validate body
    body = json.loads(event["body"])
    chat_type = body.get('chat_type')
    description = body.get('description')
    tags = body.get('tags')
    fixed_date = body.get('fixed_date')
    if not chat_type or chat_type not in ChatType.__members__:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'chat_status'"
            })
        }
    chat_type = ChatType[body['chat_type']]
    if chat_type in mandatory_date and not fixed_date:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute { fixed_date } with chat_type { %s }" % (chat_type.name)
            })
        }

    session = Session()
    chat_new = Chat(
        chat_type=chat_type, description=description,
        chat_status=ChatStatus.PENDING, tags=tags,
        senior_executive=user['email']
    )
    if fixed_date:
        chat_new.fixed_date = datetime.fromtimestamp(fixed_date).replace(hour=0, minute=0,second=0, microsecond=0)
        chat_new.chat_status = ChatStatus.ACTIVE
        edit_remaining_chats_frequency(user, access_token, -1)

    session.add(chat_new)
    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
