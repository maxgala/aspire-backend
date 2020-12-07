import json
import logging
from botocore.exceptions import ClientError
from datetime import datetime, date, timedelta, time

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import get_users, admin_update_credits
from send_email import send_email, build_calendar_invite

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
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
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

    # ACTIVE and RESERVED_PARTIAL Chats are available for booking
    # User must not have booked this Chat and must have sufficient funds
    if chat.chat_status != ChatStatus.ACTIVE and chat.chat_status != ChatStatus.RESERVED_PARTIAL:
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

    if int(user['custom:credits']) < credit_mapping[chat.chat_type]:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' does not have sufficient credits to reserve chat with id '{}'".format(user['email'], chatId)
            })
        }

    if chat.chat_type == ChatType.FOUR_ON_ONE:
        if chat.chat_status == ChatStatus.ACTIVE:
            # no prior reservations
            chat.aspiring_professionals = [user['email']]
        else:
            chat.aspiring_professionals.append(user['email'])

        if len(chat.aspiring_professionals) == 4:
            chat.chat_status = ChatStatus.RESERVED
        else:
            chat.chat_status = ChatStatus.RESERVED_PARTIAL
    else:
        chat.aspiring_professionals = [user['email']]
        chat.chat_status = ChatStatus.RESERVED

    try:
        if chat.chat_status == ChatStatus.RESERVED:
            prepare_and_send_emails(chat)
    except ClientError as e:
        session.rollback()
        session.close()
        logging.info(e)
        if int(e.response['ResponseMetadata']['HTTPStatusCode']) >= 500:
            return {
                "statusCode": 500
            }
        else:
            return {
                "statusCode": 400
            }
    else:
        admin_update_credits(user['email'], (-credit_mapping[chat.chat_type]))

        session.commit()
        session.close()
        return {
            "statusCode": 200
        }

def prepare_and_send_emails(chat):
    mentee_IDs = chat.aspiring_professionals
    mentor_ID = chat.senior_executive

    event_name = 'MAX Aspire Coffee Chat'
    event_description = chat.description

    if chat.fixed_date:
        chat_date = chat.fixed_date
    else:
        today = date.today()
        day_idx = (today.weekday() + 1) % 7 # today.weekday() is 0 for Monday
        chat_date = today + timedelta(days=7-day_idx)
    chat_time = time(14,0,0)
    event_start = datetime.combine(chat_date,chat_time)
    chat_date = f'{chat_date:%b %d, %Y}'
    event_end = event_start + timedelta(hours=12)

    mentees = []
    for m in mentee_IDs:
        m_User, _ = get_users(filter_=("email", m), attributes_filter=["given_name", "family_name"])
        mentees.append("%s %s" % (m_User['attributes']['given_name'], m_User['attributes']['family_name']))

    mentor, _ = get_users(filter_=("email", mentor_ID), attributes_filter=["given_name", "family_name"])
    mentor_name = "%s %s" % (mentor['attributes']['given_name'], mentor['attributes']['family_name'])
    mentee_name = f"{*mentees,}"
    if chat.chat_type == ChatType.FOUR_ON_ONE:
        subject = '[MAX Aspire] 4 on 1 coffee chat confirming the 4 attendees'
        mentee_body = f"Salaam!\nWe are delighted to confirm your 4 on 1 coffee chat with {mentor_name}.\nYour coffee chat will take place on: {chat_date}\n\nPlease connect with the Senior Executive to find a time that works for both of you.\nPlease make sure of your attendance. In case of any changes in the circumstances contact the support team at your earliest.\n\nBest regards,\n\nThe MAX Aspire Team"
        mentor_body = f"Salaam {mentor_name}!\n\nWe are delighted to confirm your 4 on 1 coffee chat with {mentee_name}.\n\nYour coffee chat will take place on: {chat_date}\n\nPlease connect with the Aspiring Professionals to find a time that works for both of you.\n\nIn case of any changes in the circumstances contact the support team at your earliest.\n\nBest regards,\n\nThe MAX Aspire Team"
    else:
        subject = '[MAX Aspire] 1 on 1 coffee chat'
        mentee_body = f"Salaam!\n\nWe are delighted to confirm your 1 on 1 coffee chat with {mentor_name}.\n\nYour coffee chat will take place on: {chat_date}\n\nPlease connect with the Senior Executive to find a time that works for both of you.\n\nPlease make sure of your attendance. In case of any changes in the circumstances contact the support team at your earliest.\n\nBest regards,\n\nThe MAX Aspire Team"
        mentor_body = f"Salaam {mentor_name}!\n\nWe are delighted to confirm your 1 on 1 coffee chat with {mentee_name}.\n\nYour coffee chat will take place on: {chat_date}\n\nPlease connect with the Aspiring Professional to find a time that works for both of you.\n\nIn case of any changes in the circumstances contact the support team at your earliest.\n\nBest regards,\n\nThe MAX Aspire Team"

    all_attendees = mentee_IDs.copy().append(mentor_ID)
    ics = build_calendar_invite(event_name, event_description, event_start, event_end, all_attendees)
    send_email(mentee_IDs, subject, mentee_body, ics=ics)
    # send_email(mentor_ID, subject, mentor_body, ics=ics)
    send_email('test_mentor_1@maxgala.com', subject, mentor_body, ics=ics)
