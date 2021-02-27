import json
import logging

from role_validation import UserType, check_auth
from cognito_helpers import admin_update_user_attributes
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

#TODO get value for new email

    # validate body
    body = json.loads(event["body"])
    user_email = body.get('email')
    if not user_email:
        return http_status.bad_request()

    admin_update_user_attributes(user_email,updated_email)

    return http_status.success()
