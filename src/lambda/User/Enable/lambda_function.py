import json
import logging

from role_validation import UserGroups, check_auth
from cognito_helpers import admin_enable_user

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    # validate body
    body = json.loads(event["body"])
    user_email = body.get('user_email')
    if not user_email:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'user_email'"
            })
        }

    admin_enable_user(user_email)
    return {
        "statusCode": 200
    }
