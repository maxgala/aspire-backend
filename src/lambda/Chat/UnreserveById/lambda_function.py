import json
import logging
from botocore.exceptions import ClientError

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import get_users, admin_update_credits
from send_email import send_email

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

    # to unreserve, chat must be either RESERVED_PARTIAL or RESERVED
    # in addition, user must have reserved this chat
    if chat.chat_status != ChatStatus.RESERVED_PARTIAL and chat.chat_status != ChatStatus.RESERVED:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "cannot unreserve inactive or unreserved chat with id '{}'".format(chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }
    if not chat.aspiring_professionals or user['email'] not in chat.aspiring_professionals:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' did not reserve chat with id '{}'".format(user['email'], chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    chat.aspiring_professionals.remove(user['email'])
    if not chat.aspiring_professionals:
        chat.chat_status = ChatStatus.ACTIVE
    else:
        chat.chat_status = ChatStatus.RESERVED_PARTIAL

    try:
        # FIXME send email to both
        prepare_and_send_email_to_ap(user['email'], user['email'])
        prepare_and_send_email_to_se(user['email'], user['email'])
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
        admin_update_credits(user['email'], credit_mapping[chat.chat_type])

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

def prepare_and_send_email_to_ap(ap, se):
    return
    mentor, _ = get_users(filter_=("email", se), attributes_filter=["given_name", "family_name"])
    mentor_name = "%s %s" % (mentor['attributes']['given_name'], mentor['attributes']['family_name'])

    subject = '[MAX Aspire] Coffee chat unreserved'
    mentee_body = f"Salaam,\n\nWe have received your cancellation request, and thus can confirm that your reserved coffee chat with the Senior Executive {mentor_name} is now cancelled.\n\nYou can login to your account to purchase credits and book any future coffee chats.\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"
    send_email(ap, subject, mentee_body)

def prepare_and_send_email_to_se(ap, se):
    return
    mentee, _ = get_users(filter_=("email", ap), attributes_filter=["given_name", "family_name"])
    mentee_name = "%s %s" % (mentee['attributes']['given_name'], mentee['attributes']['family_name'])

    subject = '[MAX Aspire] Coffee chat unreserved'
    mentor_body = f"Salaam,\n\nWe have received your cancellation request, and thus can confirm that your reserved coffee chat with the Aspiring Professional(s) {mentee_name} is now cancelled.\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"
    send_email(se, subject, mentor_body)
    #send_email('test_mentor_1@maxgala.com', subject, mentor_body)
