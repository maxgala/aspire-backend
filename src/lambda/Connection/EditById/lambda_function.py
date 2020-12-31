import json
import logging

from connection import Connection, ConnectionStatus
from base import Session, row2dict
from send_email import send_email
from role_validation import UserType, check_auth
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.FREE,
        UserType.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    connectId = event["pathParameters"].get("connectId") if event["pathParameters"] else None
    if not connectId:
        return http_status.bad_request("missing path parameter(s): 'connectId'")

    session = Session()
    connection = session.query(Connection).get(connectId)
    if not connection:
        session.close()
        return http_status.not_found()

    body = json.loads(event["body"])
    new_connection_status = body.get('connect_status')
    if new_connection_status and new_connection_status not in ConnectionStatus.__members__:
        session.close()
        return http_status.bad_request("invalid parameter(s): 'connect_status'")

    if new_connection_status:
        if connection.connect_status == ConnectionStatus.PENDING and new_connection_status == 'ACCEPTED':
            # TODO: dynamic user_email
            # TODO: update email subject/body
            user_email = "saleh.bakhit@hotmail.com"
            email_subject = "Your Senior Executive connection request was accepted"
            email_body = "<name> has accepted your connection request!"
            send_email(to_addresses=user_email, subject=email_subject, body_text=email_body)

        connection.connect_status = ConnectionStatus[new_connection_status]

    session.commit()
    session.refresh(connection)
    session.close()

    return http_status.success(json.dumps(
            row2dict(connection)
        ))
