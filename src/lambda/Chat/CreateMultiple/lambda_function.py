import json
import logging
from datetime import datetime

from chat import Chat, ChatType, ChatStatus, mandatory_date
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_declared_chats_frequency

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    # validate body
    body = json.loads(event["body"])
    senior_executive = body.get('senior_executive')
    chats_new = body.get('chats')
    if not senior_executive or not chats_new:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'senior_executive, chats'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    session = Session()
    for chat_new in chats_new:
        if not chat_new.get('chat_type') or chat_new['chat_type'] not in ChatType.__members__:
            session.close()
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "errorMessage": "invalid parameter(s): 'chat_type'"
                }),
                "headers": {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                    'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                }
            }

        chat_type = ChatType[chat_new['chat_type']]
        description = chat_new.get('description')
        tags = chat_new.get('tags')
        fixed_date = chat_new.get('fixed_date')
        if chat_type in mandatory_date and not fixed_date:
            session.rollback()
            session.close()
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "errorMessage": "missing body attribute { fixed_date } with chat_type { %s }" % (chat_type.name)
                }),
                "headers": {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                    'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                }
            }

        chat = Chat(
            chat_type=chat_type, description=description,
            chat_status=ChatStatus.PENDING, tags=tags,
            senior_executive=senior_executive
        )

        admin_update_declared_chats_frequency(senior_executive, 1)
        if fixed_date:
            chat.fixed_date = datetime.fromtimestamp(fixed_date).replace(hour=0, minute=0,second=0, microsecond=0)
            chat.chat_status = ChatStatus.ACTIVE
        else:
            admin_update_remaining_chats_frequency(senior_executive, 1)
        session.add(chat)

    session.commit()
    session.close()

    return {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
        }
    }
