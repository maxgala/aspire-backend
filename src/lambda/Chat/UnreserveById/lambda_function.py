import json
import logging
import boto3
from botocore.exceptions import ClientError

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserGroups, check_auth
from cognito_helpers import admin_update_credits
from send_email import send_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('cognito-idp')
USER_POOL_ID = 'us-east-1_OiH5DGpGX'

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.FREE,
        UserGroups.PAID
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_groups)

    print("checking user in unreservebyid")
    print(user)

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

    # to unreserve, chat must be either ACTIVE(multi aspiring professional chats) or RESERVED(single aspiring professional chats)
    # in addition, user must have reserved this chat
    #
    # if chat_status is RESERVED => set to ACTIVE
    if not ((chat.chat_type == ChatType.FOUR_ON_ONE and chat.chat_status == ChatStatus.ACTIVE) \
        or (chat.chat_type != ChatType.FOUR_ON_ONE and chat.chat_status == ChatStatus.RESERVED)):
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "cannot unreserve inactive or unreserved chat with id '{}'".format(chatId)
            })
        }
    if not chat.aspiring_professionals or user['email'] not in chat.aspiring_professionals:
        session.close()
        return {
            "statusCode": 403,
            "body": json.dumps({
                "errorMessage": "user '{}' did not reserve chat with id '{}'".format(user['email'], chatId)
            })
        }

    print('aspiring_professionals 1')
    print(chat.aspiring_professionals)
    if user['email'] in chat.aspiring_professionals:
        chat.aspiring_professionals.remove(user['email'])
        print('aspiring_professionals 2')
        print(chat.aspiring_professionals)
        prepare_and_send_email_to_ap(user['email'], chat.senior_executive)
        prepare_and_send_email_to_se(user['email'], chat.senior_executive)

    print('aspiring_professionals 3')
    print(chat.aspiring_professionals)
    if (chat.chat_type != ChatType.ONE_ON_ONE and chat.chat_status == ChatStatus.RESERVED) \
        or (chat.chat_type != ChatType.FOUR_ON_ONE and (chat.aspiring_professionals is None \
        or len(chat.aspiring_professionals) == 0)):
        chat.chat_status = ChatStatus.ACTIVE


    session.commit()
    session.close()

    return {
        "statusCode": 200
    }


def prepare_and_send_email_to_ap(ap, se):

    mentor = client.admin_get_user(
        UserPoolId = USER_POOL_ID,
        Username = se
    )

    mentee = client.admin_get_user(
        UserPoolId = USER_POOL_ID,
        Username = ap
    )

    mentor_name = get_full_name(mentor)
    mentee_name = get_full_name(mentee)

    subject = '[MAX Aspire] Coffee chat unreserved'
    mentee_body = f"Salaam,\n\nWe have received your cancellation request, and thus can confirm that your reserved coffee chat with the Senior Executive {mentor_name} is now cancelled.\n\nPlease note that any credits spent on the coffee chat are non refundable. You can login to your account to purchase credits and book any future coffee chats.\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"

    send_email(ap, subject, mentee_body)

def prepare_and_send_email_to_se(ap, se):

    mentor = client.admin_get_user(
        UserPoolId = USER_POOL_ID,
        Username = se
    )

    mentee = client.admin_get_user(
        UserPoolId = USER_POOL_ID,
        Username = ap
    )

    mentee_name = get_full_name(mentee)

    subject = '[MAX Aspire] Coffee chat unreserved'
    mentor_body = f"Salaam,\n\nWe have received your cancellation request, and thus can confirm that your reserved coffee chat with the Aspiring Professional(s) {mentee_name} is now cancelled.\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"

    send_email(se, subject, mentor_body)

def prepare_and_send_email(chat):

    # print('starting the unreserve script')
    # print(chat)

    mentee_IDs = chat.aspiring_professionals 
    mentor_ID = chat.senior_executive 

    mentor = client.admin_get_user(
        UserPoolId = USER_POOL_ID,
        Username = mentor_ID
    )

    mentees = []
    for m in mentee_IDs:
        try: 
            m_User = client.admin_get_user(
                UserPoolId = USER_POOL_ID,
                Username = m
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        mentees.append(get_full_name(m_User))

    mentor_name = get_full_name(mentor)
    mentee_name = f"{*mentees,}"

    subject = '[MAX Aspire] Coffee chat unreserved'
    mentee_body = f"Salaam,\n\nWe have received your cancellation request, and thus can confirm that your reserved coffee chat with the Senior Executive {mentor_name} is now cancelled.\n\nPlease note that any credits spent on the coffee chat are non refundable. You can login to your account to purchase credits and book any future coffee chats.\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"

    mentor_body = f"Salaam,\n\nWe have received your cancellation request, and thus can confirm that your reserved coffee chat with the Aspiring Professional(s) {mentee_name} is now cancelled.\n\nThank you.\n\nBest regards,\n\nThe MAX Aspire Team"

    send_email(mentee_IDs, subject, mentee_body)
    send_email(mentor_ID, subject, mentor_body)

def get_full_name(user):
    user_data = user['UserAttributes']
    for i in user_data:
        if i['Name'] == 'given_name':
            given = i['Value']
        elif i['Name'] == 'family_name':
            family = i['Value']
    return given + " " + family
