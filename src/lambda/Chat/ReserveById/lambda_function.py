import json
import logging
from botocore.exceptions import ClientError
from datetime import datetime, date, timedelta, time

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import get_users, admin_update_credits
from send_email import send_templated_email
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    authorized_user_types = [
        UserType.FREE,
        UserType.PAID
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)

    if not success:
        return http_status.unauthorized("Thank-you so kindly for being a MAX Aspire member. To support our operational costs, this specific feature is available if you sign up for a paid plan or purchase credits")

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return http_status.bad_request("missing path parameter(s): 'chatId'")

    session = Session()
    chat = session.query(Chat).get(chatId)
    if not chat:
        session.close()
        return http_status.not_found("chat with id '{}' not found".format(chatId))

    # ACTIVE Chats are available for booking
    # User must not have booked this Chat and must have sufficient funds
    if chat.chat_status != ChatStatus.ACTIVE:
        session.close()
        return http_status.forbidden("Chat is not available for booking")

    if chat.aspiring_professionals and user['email'] in chat.aspiring_professionals:
        session.close()
        return http_status.forbidden("user '{}' already reserved chat with id '{}'".format(user['email'], chatId))

    user_credits = int(get_users(filter_=("email", user['email']), \
        attributes_filter=["custom:credits"])[0]['attributes'].get('custom:credits'))
    if user_credits < credit_mapping[chat.chat_type]:
        session.close()
        return http_status.forbidden("Thank-you so kindly for being a MAX Aspire member. To support our operational costs, this specific feature is available if you sign up for a paid plan or purchase credits")

    chat.aspiring_professionals = [user['email']]
    chat.chat_status = ChatStatus.RESERVED

    try:
        prepare_and_send_emails(chat)
    except ClientError as e:
        session.rollback()
        session.close()
        logging.info(e)
        if int(e.response['ResponseMetadata']['HTTPStatusCode']) >= 500:
            return http_status.server_error()
        else:
            return http_status.bad_request()
    else:
        admin_update_credits(user['email'], (-credit_mapping[chat.chat_type]))

        session.commit()
        session.close()
        return http_status.success()

def prepare_and_send_emails(chat):
    mentee_email = chat.aspiring_professionals[0].strip()
    mentor_email = chat.senior_executive.strip()

    mentee, _ = get_users(filter_=("email", mentee_email), attributes_filter=["given_name", "family_name"])
    mentee_name = "%s %s" % (mentee['attributes']['given_name'], mentee['attributes']['family_name'])

    mentor, _ = get_users(filter_=("email", mentor_email), attributes_filter=["given_name", "family_name"])
    mentor_name = "%s %s" % (mentor['attributes']['given_name'], mentor['attributes']['family_name'])

    chat_type = ''
    if chat.chat_type == ChatType.MOCK_INTERVIEW:
        chat_type = 'Mock Interview'
    else:
        chat_type = 'One-on-One coffee chat'

    template_data = {
        "mentor_email": mentor_name,
        "mentee_email": mentee_email,
        "mentor_name": mentor_name,
        "mentee_name": mentee_name,
        "chat_type": chat_type
    }
    template_data = json.dumps(template_data)
    recipients = [mentee_email, mentor_name]
    send_templated_email(recipients, "Chat-Reservation", template_data)