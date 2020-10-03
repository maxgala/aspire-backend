import json
import logging

from connect_se import ConnectSE
from base import Session, row2dict
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

    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    requestor_filter = event["queryStringParameters"].get("requestor", "") if event["queryStringParameters"] else ""
    requestee_filter = event["queryStringParameters"].get("requestee", "") if event["queryStringParameters"] else ""

    session = Session()
    filtered_query = session.query(ConnectSE)
    if status_filter:
        filtered_query = filtered_query.filter(ConnectSE.connect_status == status_filter)
    if requestor_filter:
        filtered_query = filtered_query.filter(ConnectSE.requestor == requestor_filter)
    if requestee_filter:
        filtered_query = filtered_query.filter(ConnectSE.requestee == requestee_filter)

    connect_ses = filtered_query.all()
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "connect_ses": [row2dict(r) for r in connect_ses],
            "count": len(connect_ses)
        })
    }
