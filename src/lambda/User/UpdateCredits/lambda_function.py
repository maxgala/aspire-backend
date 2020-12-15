import json
import logging

from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import admin_update_credits
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    authorized_user_types = [
        UserType.ADMIN,
        UserType.PAID,
        UserType.FREE
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    body = json.loads(event["body"])
    user_email = body.get('email')
    user_credits = body.get('credits')
    if not user_email or not credits or not isinstance(user_credits, int):
        return http_status.bad_request()

    success = edit_auth(user, user_email)
    if not success:
        return http_status.unauthorized()

    admin_update_credits(user_email, user_credits)
    return http_status.success()