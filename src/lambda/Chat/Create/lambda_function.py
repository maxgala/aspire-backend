import json
import logging
from datetime import datetime

from chat import Chat, ChatType, ChatStatus, credit_mapping, mandatory_date
from base import Session
from role_validation import UserGroups, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # validate authorization
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

    # validate body
    body = json.loads(event["body"])
    chat_type = body.get('chat_type')
    description = body.get('description')
    tags = body.get('tags')
    date = body.get('date')
    if not chat_type or chat_type not in ChatType.__members__:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'chat_status'"
            })
        }
    chat_type = ChatType[body['chat_type']]
    if chat_type in mandatory_date and not date:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute { date } with chat_type { %s }" % (chat_type.name)
            })
        }

    # TODO: remove credits
    session = Session()
    chat_new = Chat(
        chat_type=chat_type, description=description,
        credits=credit_mapping[chat_type], chat_status=ChatStatus.PENDING,
        senior_executive=user['email'], tags=tags
    )
    if date:
        chat_new.date = datetime.fromtimestamp(date).replace(hour=0, minute=0,second=0, microsecond=0),
        chat_new.end_date = chat_new.date

    session.add(chat_new)
    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
