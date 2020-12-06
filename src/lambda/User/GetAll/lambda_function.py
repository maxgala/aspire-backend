import json
import logging

from role_validation import UserType
from cognito_helpers import get_users

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# TODO: Is it safe to return all the user's info since this endpoint is not protected?
def handler(event, context):
    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""

    if status_filter and status_filter in ['Enabled', 'Disabled']:
        filter_ = ('status', status_filter)
    else:
        filter_ = ('status', 'Enabled')
    if type_filter and type_filter in UserType.__members__:
        user_type = type_filter
    else:
        user_type = None

    users, count = get_users(filter_=filter_, user_type=user_type)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "users": users,
            "count": count
        })
    }
