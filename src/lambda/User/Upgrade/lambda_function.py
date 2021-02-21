import json
import logging

from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import admin_update_credits, admin_update_user_attributes
import http_status
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    authorized_user_types = [
        UserType.ADMIN,
        UserType.FREE
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    user_email = user['email']
    if not user_email:
        return http_status.bad_request()

    success = edit_auth(user, user_email)
    if not success:
        return http_status.unauthorized()

    current_timestamp = int(datetime.now().timestamp())
    
    attributes = {
        "custom:user_type": "PAID",
        "custom:start_date" : str(current_timestamp),
        "custom:end_date": str(current_timestamp + 31556952) # 31556952 is the seconds in a year
    }
    admin_update_user_attributes(user_email,attributes)
    user_credits = 25
    admin_update_credits(user_email, user_credits)
    return http_status.success()