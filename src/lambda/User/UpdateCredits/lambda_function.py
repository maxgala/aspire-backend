import json
import logging

from role_validation import UserGroups, check_auth, edit_auth
from cognito_helpers import admin_update_credits

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.PAID,
        UserGroups.FREE
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_groups)
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
    user_credits = body.get('credits')
    if not user_email or not credits or not isinstance(user_credits, int):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'email, credits'"
            })
        }

    success = edit_auth(user, user_email)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    admin_update_credits(user_email, user_credits)
    return {
        "statusCode": 200
    }
