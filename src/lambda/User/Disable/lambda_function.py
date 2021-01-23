import json
import logging

from role_validation import UserType, check_auth
from cognito_helpers import admin_disable_user
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    authorized_user_types = [
        UserType.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    body = json.loads(event["body"])
    user_email = body.get('email')
    if not user_email:
        return http_status.bad_request()

    admin_disable_user(user_email)
    # TODO: should we remove the user's chats/jobs etc...?
    return http_status.success()