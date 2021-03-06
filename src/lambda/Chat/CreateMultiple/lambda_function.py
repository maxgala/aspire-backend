import json
import logging
from datetime import datetime

from chat import Chat, ChatType, ChatStatus, mandatory_date
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_declared_chats_frequency
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.forbidden()

    # validate body
    body = json.loads(event["body"])
    senior_executive = body.get('senior_executive')
    chats_new = body.get('chats')
    if not senior_executive or not chats_new:
        return http_status.bad_request("invalid parameter(s): 'senior_executive, chats'")

    session = Session()
    for chat_new in chats_new:
        if not chat_new.get('chat_type') or chat_new['chat_type'] not in ChatType.__members__:
            session.close()
            return http_status.bad_request("invalid parameter(s): 'chat_type'")

        chat_type = ChatType[chat_new['chat_type']]
        description = chat_new.get('description')
        tags = chat_new.get('tags')
        fixed_date = chat_new.get('fixed_date')
        if chat_type in mandatory_date and not fixed_date:
            session.rollback()
            session.close()
            return http_status.bad_request("missing body attribute { fixed_date } with chat_type { %s }" % (chat_type.name))

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

    return http_status.success()