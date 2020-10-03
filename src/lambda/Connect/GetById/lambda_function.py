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
    session.close()
    if not connect_se:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "connect senior executive with id '{}' not found".format(connectId)
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(connect_se)
        )
    }
