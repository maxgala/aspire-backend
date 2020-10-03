import json
import logging

from connect_se import ConnectSE, ConnectStatus
from base import Session
from send_email import send_email
# from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_groups = [
    #     UserGroups.ADMIN,
    #     UserGroups.MENTOR,
    #     UserGroups.FREE,
    #     UserGroups.PAID
    # ]
    # err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    # if err:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": group_response
    #         })
    #     }

    body = json.loads(event["body"])
    requestor = body.get('requestor')
    requestee = body.get('requestee')

    if not requestor:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'requestor'"
            })
        }
    if not requestee:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'requestee'"
            })
        }

    ConnectSE_new = ConnectSE(requestor=requestor, requestee=requestee, connect_status=ConnectStatus.PENDING)

    # TODO: dynamic user_email
    # TODO: update email subject/body
    user_email = "saleh.bakhit@hotmail.com"
    email_subject = "You have received a new Senior Executive connection request"
    email_body = "<name> has requested to connect with you"
    send_email(to_addresses=user_email, subject=email_subject, body_text=email_body)

    session = Session()
    session.add(ConnectSE_new)
    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
