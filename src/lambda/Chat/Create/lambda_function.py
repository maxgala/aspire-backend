import json
import logging
from datetime import datetime

from chat import Chat, ChatType, ChatStatus, mandatory_date
from base import Session
from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_declared_chats_frequency

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
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    # validate body
    body = json.loads(event["body"])
    if not body.get('senior_executive') or not body.get('chat_type') or body['chat_type'] not in ChatType.__members__:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'senior_executive, chat_type'"
            })
        }

    senior_executive = body['senior_executive']
    success = edit_auth(user, senior_executive)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    chat_type = ChatType[body['chat_type']]
    description = body.get('description')
    tags = body.get('tags')
    fixed_date = body.get('fixed_date')
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
        senior_executive=senior_executive
    )

    admin_update_declared_chats_frequency(senior_executive, 1)
    if fixed_date:
        chat_new.fixed_date = datetime.fromtimestamp(fixed_date).replace(hour=0, minute=0,second=0, microsecond=0)
        chat_new.chat_status = ChatStatus.ACTIVE
    else:
        admin_update_remaining_chats_frequency(senior_executive, 1)

    session.add(chat_new)
    session.commit()
    session.close()

    return {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
        }
    }
