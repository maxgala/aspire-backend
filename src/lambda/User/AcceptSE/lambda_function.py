import json
import logging

from role_validation import UserType, check_auth
from cognito_helpers import admin_update_user_attributes, admin_enable_user
import http_status
from datetime import datetime
from chat import Chat, ChatType, ChatStatus
from base import Session

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    authorized_user_types = [
        UserType.ADMIN,
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    body = json.loads(event["body"])
    user_email = body.get('email')
    if not user_email:
        return http_status.bad_request()
    
    chat_freq = 4
    attributes = {
        "custom:user_type": "MENTOR",
        "custom:declared_chats_freq" : str(chat_freq),
        "custom:remaining_chats_freq" : str(chat_freq)
    }
    admin_update_user_attributes(user_email,attributes)
    admin_enable_user(user_email)

    session = Session()
    for i in range(chat_freq):
        chat_type = ChatType["ONE_ON_ONE"]
        chat = Chat(
            chat_type=chat_type,
            chat_status=ChatStatus.PENDING,
            senior_executive=user_email
        )
        session.add(chat)

    session.commit()
    session.close()

    return http_status.success()