import json
import logging

from role_validation import UserType, check_auth
from cognito_helpers import admin_enable_user

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
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    # validate body
    body = json.loads(event["body"])
    user_email = body.get('email')
    if not user_email:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "invalid parameter(s): 'email'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    admin_enable_user(user_email)
    return {
        "statusCode": 200,
        "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
    }
