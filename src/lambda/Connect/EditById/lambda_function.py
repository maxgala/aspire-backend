import json
import logging

from connect_se import ConnectSE, ConnectStatus
from base import Session, row2dict
from send_email import send_email
# from role_validation import UserType, check_auth
from common import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_user_types = [
    #     UserType.ADMIN,
    #     UserType.MENTOR,
    #     UserType.FREE,
    #     UserType.PAID
    # ]
    # success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    # if not success:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": "unauthorized"
    #         })
    #     }

    connectId = event["pathParameters"].get("connectId") if event["pathParameters"] else None
    if not connectId:
        return http_status.bad_request("missing path parameter(s): 'connectId'")

    session = Session()
    connect_se = session.query(ConnectSE).get(connectId)
    if not connect_se:
        session.close()
        return http_status.not_found()

    body = json.loads(event["body"])
    connect_status_new = body.get('connect_status')
    if connect_status_new and connect_status_new not in ConnectStatus.__members__:
        session.close()
        return http_status.bad_request("invalid parameter(s): 'connect_status'")

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

    return http_status.success(json.dumps(
            row2dict(connect_se)
        ))
