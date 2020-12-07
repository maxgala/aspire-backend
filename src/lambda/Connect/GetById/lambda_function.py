import json
import logging

from connect_se import ConnectSE
from base import Session, row2dict
# from role_validation import UserType, check_auth

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
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'connectId'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
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
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(connect_se)
        ),
        "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
    }
