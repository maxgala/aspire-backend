import json
import logging

from connect import Connection
from base import Session
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

    session.delete(connection)
    session.commit()
    session.close()

    return http_status.success()
