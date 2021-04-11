import json
import logging

from role_validation import UserType
from cognito_helpers import get_users_pagination
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""
    page_limit = event["queryStringParameters"].get("limit", "20") if event["queryStringParameters"] else "20"
    pagination_token = event["queryStringParameters"].get("token", None) if event["queryStringParameters"] else None

    if status_filter and status_filter in ['Enabled', 'Disabled']:
        filter_ = ('status', status_filter)
    else:
        filter_ = ('status', 'Enabled')
    if type_filter:
        user_type = [x.strip() for x in type_filter.split(',') if x in UserType.__members__]
    else:
        user_type = None

    users, count, pagination_response_token = get_users_pagination(filter_=filter_, user_type=user_type, pagination_token=pagination_token,limit=int(page_limit))
    _users = users.values()
    return http_status.success(json.dumps({
            "users": list(_users),
            "count": count,
            "pagination_token": pagination_response_token
        }))
