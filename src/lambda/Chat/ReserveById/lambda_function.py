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
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'chatId'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    session = Session()
    chat = session.query(Chat).get(chatId)
    if not chat:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "chat with id '{}' not found".format(chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    # ACTIVE and RESERVED_PARTIAL Chats are available for booking
    # User must not have booked this Chat and must have sufficient funds
    if chat.chat_status != ChatStatus.ACTIVE and chat.chat_status != ChatStatus.RESERVED_PARTIAL:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "cannot reserve inactive chat with id '{}'".format(chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }
    if chat.aspiring_professionals and user['email'] in chat.aspiring_professionals:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' already reserved chat with id '{}'".format(user['email'], chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    if int(user['custom:credits']) < credit_mapping[chat.chat_type]:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' does not have sufficient credits to reserve chat with id '{}'".format(user['email'], chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
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
        if chat.chat_status == ChatStatus.RESERVED or chat.chat_status == ChatStatus.RESERVED_PARTIAL:
            prepare_and_send_emails(chat)
    except ClientError as e:
        session.rollback()
        session.close()
        logging.info(e)
        if int(e.response['ResponseMetadata']['HTTPStatusCode']) >= 500:
            return {
                "statusCode": 500,
                "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
            }
        else:
            return {
                "statusCode": 400,
                "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
            }
    else:
        admin_update_credits(user['email'], (-credit_mapping[chat.chat_type]))

        session.commit()
        session.close()
        return {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

def prepare_and_send_emails(chat):
    mentee_IDs = chat.aspiring_professionals
    mentor_ID = chat.senior_executive

    event_name = '[MAX Aspire] Coffee Chat with Senior Executive'
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

    chat_type = ''
    if chat.chat_type == ChatType.FOUR_ON_ONE:
        chat_type = '4-on-1'
    else:
        chat_type = '1-on-1'

    subject = '[MAX Aspire] Your coffee chat is confirmed!'
    body = f"Salaam!\nWe are delighted to confirm your {chat_type} coffee chat with {mentor_name}.\n\nYour coffee chat will take place on: {chat_date}. Please connect with the Senior Executive to find a time that works for both of you.\n\nPlease make sure of your attendance. In case of any changes in the circumstances contact the support team at your earliest.\n\nBest regards,\n\nThe MAX Aspire Team"
    # TODO change mentor recipient to mentor_ID
    mentor_ID = 'test_mentor_1@maxgala.com'
    all_attendees = list(mentee_IDs)
    all_attendees.append(mentor_ID)
    ics = build_calendar_invite(event_name, event_description, event_start, event_end, all_attendees)
    send_email(all_attendees, subject, body, ics=ics)
