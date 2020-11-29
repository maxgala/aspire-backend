import json
import logging

from cognito_helpers import get_users

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    userId = event["pathParameters"].get("userId") if event["pathParameters"] else None
    if not userId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'chatId'"
            })
        }

    user, _ = get_users(filter_=('email', userId))
    if not user:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "chat with id '{}' not found".format(userId)
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps(user)
    }
