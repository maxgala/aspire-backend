import json
import logging

from connect_se import ConnectSE
from base import Session
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

    session.delete(connect_se)
    session.commit()
    session.close()

    return http_status.success()
