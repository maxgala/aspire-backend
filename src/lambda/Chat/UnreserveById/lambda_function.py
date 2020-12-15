import json
import logging
from botocore.exceptions import ClientError

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import get_users, admin_update_credits
from send_email import send_email
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.FREE,
        UserType.PAID
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)

    if not success:
        return http_status.unauthorized()

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return http_status.bad_request("missing path parameter(s): 'chatId'")

    session = Session()
    chat = session.query(Chat).get(chatId)
    if not chat:
        session.close()
        return http_status.not_found("chat with id '{}' not found".format(chatId))

    # to unreserve, chat must be either RESERVED_PARTIAL or RESERVED
    # in addition, user must have reserved this chat
    if chat.chat_status != ChatStatus.RESERVED_PARTIAL and chat.chat_status != ChatStatus.RESERVED:
        session.close()
        return http_status.forbidden("cannot unreserve inactive or unreserved chat with id '{}'".format(chatId))
    if not chat.aspiring_professionals or user['email'] not in chat.aspiring_professionals:
        session.close()
        return http_status.forbidden("user '{}' did not reserve chat with id '{}'".format(user['email'], chatId))

    chat.aspiring_professionals.remove(user['email'])
    if not chat.aspiring_professionals:
        chat.chat_status = ChatStatus.ACTIVE
    else:
        chat.chat_status = ChatStatus.RESERVED_PARTIAL

    try:
        # FIXME send email to both
        se = chat.senior_executive
        se = 'test_mentor_1@maxgala.com'
        prepare_and_send_email(user['email'], se)
    except ClientError as e:
        session.rollback()
        session.close()
        logging.info(e)
        if int(e.response['ResponseMetadata']['HTTPStatusCode']) >= 500:
            return http_status.server_error()
        else:
            return http_status.bad_request()
    else:
        admin_update_credits(user['email'], credit_mapping[chat.chat_type])

        session.commit()
        session.close()
        return http_status.success()

def prepare_and_send_email(ap, se):
    subject = '[MAX Aspire] Unreserved coffee chat'
    body = f"Salaam,\n\nAs requested, we have cancelled your coffee chat. Please use the platform to connect with other members!\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"
    send_email([ap, se], subject, body)