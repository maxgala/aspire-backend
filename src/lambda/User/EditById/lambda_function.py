import json
import logging

from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import get_users, admin_update_user_attributes
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

standard_attributes = [
    'address', 'birthdate', 'email', 'family_name', 'gender', 'given_name', 'locale',
    'middle_name', 'name', 'nickname', 'phone_number', 'picture', 'preferred_username',
    'profile', 'updated_at', 'website', 'zoneinfo'
]

def handler(event, context):
    authorized_user_types = [
        UserType.MENTOR,
        UserType.PAID,
        UserType.FREE
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    userId = event["pathParameters"].get("userId") if event["pathParameters"] else None
    if not userId:
        return http_status.bad_request()

    user_edit, _ = get_users(filter_=('email', userId))
    if not user_edit:
        return http_status.not_found()
    user_attributes = user_edit['attributes']
    success = edit_auth(user, user_attributes.pop('email'))
    if not success:
        return http_status.unauthorized()

    body = json.loads(event["body"])

    user_type = user['custom:user_type']
    if user_type == 'MENTOR':
        body['custom:resume'] = 'https://aspire-user-profile.s3.amazonaws.com/blank_resume.pdf'

    new_attrs = {}
    for key in body:
        if key not in standard_attributes:
            key = 'custom:' + key
        new_attrs[key] = body[key]

    admin_update_user_attributes(user['email'], new_attrs)
    return http_status.success(json.dumps(user))
