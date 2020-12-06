import json
import logging

from role_validation import UserType, check_auth
from cognito_helpers import admin_disable_user

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    # validate body
    body = json.loads(event["body"])
    user_email = body.get('email')
    if not user_email:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'email'"
            })
        }

    admin_disable_user(user_email)
    # TODO: should we remove the user's chats/jobs etc...?
    return {
        "statusCode": 200
    }
