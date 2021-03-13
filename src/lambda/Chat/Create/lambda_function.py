import json
import logging
from datetime import datetime

from chat import Chat, ChatType, ChatStatus, mandatory_date
from base import Session
from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import admin_update_remaining_chats_frequency, admin_update_declared_chats_frequency
import http_status

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
        return http_status.unauthorized()

    # validate body
    body = json.loads(event["body"])
    if not body.get('senior_executive') or not body.get('chat_type') or body['chat_type'] not in ChatType.__members__:
        return http_status.bad_request("invalid parameter(s): 'senior_executive, chat_type'")

    senior_executive = body['senior_executive']
    success = edit_auth(user, senior_executive)
    if not success:
        return http_status.unauthorized()

    chat_type = ChatType[body['chat_type']]
    description = body.get('description')
    tags = body.get('tags')
    fixed_date = body.get('fixed_date')
    if chat_type in mandatory_date and not fixed_date:
        return http_status.bad_request("missing body attribute { fixed_date } with chat_type { %s }" % (chat_type.name))
 
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

    return http_status.success()