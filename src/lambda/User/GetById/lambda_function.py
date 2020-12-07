import json
import logging

from cognito_helpers import get_users

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# TODO: Is it safe to return all the user's info since this endpoint is not protected?
def handler(event, context):
    userId = event["pathParameters"].get("userId") if event["pathParameters"] else None
    if not userId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'userId'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    user, _ = get_users(filter_=('email', userId))
    if not user:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "user with id '{}' not found".format(userId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps(user),
        "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
    }
