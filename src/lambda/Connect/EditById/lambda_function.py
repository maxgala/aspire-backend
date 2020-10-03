import json
import logging

from connect_se import ConnectSE, ConnectStatus
from base import Session, row2dict
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

    connectId = event["pathParameters"].get("connectId") if event["pathParameters"] else None
    if not connectId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'connectId'"
            })
        }

    session = Session()
    connect_se = session.query(ConnectSE).get(connectId)
    if not connect_se:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "connect senior executive with id '{}' not found".format(connectId)
            })
        }

    body = json.loads(event["body"])
    connect_status_new = body.get('connect_status')
    if connect_status_new and connect_status_new not in ConnectStatus.__members__:
        session.close()
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'connect_status'"
            })
        }

    if connect_status_new:
        if connect_se.connect_status == ConnectStatus.PENDING and connect_status_new == 'ACCEPTED':
            # TODO: dynamic user_email
            # TODO: update email subject/body
            user_email = "saleh.bakhit@hotmail.com"
            email_subject = "Your Senior Executive connection request was accepted"
            email_body = "<name> has accepted your connection request!"
            send_email(to_addresses=user_email, subject=email_subject, body_text=email_body)

        connect_se.connect_status = ConnectStatus[connect_status_new]

    session.commit()
    session.refresh(connect_se)
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(connect_se)
        )
    }

