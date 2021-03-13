import json
import logging

from role_validation import UserType
from cognito_helpers import get_users
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""

    if status_filter and status_filter in ['Enabled', 'Disabled']:
        filter_ = ('status', status_filter)
    else:
        filter_ = ('status', 'Enabled')
    if type_filter:
        user_type = [x.strip() for x in type_filter.split(',') if x in UserType.__members__]
    else:
        user_type = None

    users, count = get_users(filter_=filter_, user_type=user_type)
    _users = users.values()
    return http_status.success(json.dumps({
            "users": _users,
            "count": count
        }))
