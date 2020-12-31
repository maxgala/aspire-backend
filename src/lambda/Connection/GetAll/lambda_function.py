import json
import logging

from connection import Connection
from base import Session, row2dict
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

    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    requestor_filter = event["queryStringParameters"].get("requestor", "") if event["queryStringParameters"] else ""
    requestee_filter = event["queryStringParameters"].get("requestee", "") if event["queryStringParameters"] else ""

    session = Session()
    filtered_query = session.query(Connection)
    if status_filter:
        filtered_query = filtered_query.filter(Connection.connect_status == status_filter)
    if requestor_filter:
        filtered_query = filtered_query.filter(Connection.requestor == requestor_filter)
    if requestee_filter:
        filtered_query = filtered_query.filter(Connection.requestee == requestee_filter)

    connections = filtered_query.all()
    session.close()

    return http_status.success(json.dumps({
            "connections": [row2dict(r) for r in connections],
            "count": len(connections)
        }))
