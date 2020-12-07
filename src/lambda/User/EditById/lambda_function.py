import json
import logging

from role_validation import UserType, check_auth, edit_auth
from cognito_helpers import get_users, admin_update_user_attributes

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.MENTOR,
        UserType.PAID,
        UserType.FREE
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    userId = event["pathParameters"].get("userId") if event["pathParameters"] else None
    if not userId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'userId'"
            })
        }

    user_edit, _ = get_users(filter_=('email', userId))
    if not user_edit:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "user with id '{}' not found".format(userId)
            })
        }
    user_attributes = user_edit['attributes']
    success = edit_auth(user, user_attributes.pop('email'))
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    body = json.loads(event["body"])
    # phone_number = body.get('phone_number')
    # birthdate = body.get('birthdate')
    # industry = body.get('industry')
    # industry_tags = body.get('industry_tags')
    # position = body.get('position')
    # company = body.get('company')
    # education_level = body.get('education_level')
    # resume = body.get('resume')
    # linkedin = body.get('linkedin')

    user_attributes['given_name'] = body.get('given_name') if body.get('given_name') else user_attributes['given_name']
    user_attributes['family_name'] = body.get('family_name') if body.get('family_name') else user_attributes['family_name']
    user_attributes['custom:prefix'] = body.get('prefix') if body.get('prefix') else user_attributes['custom:prefix']
    user_attributes['gender'] = body.get('gender') if body.get('gender') else user_attributes['gender']
    user_attributes['picture'] = body.get('picture') if body.get('picture') else user_attributes['picture']

    address = json.loads(user_attributes['address'])
    address['country'] = body.get('country') if body.get('country') else address.get('country')
    address['region'] = body.get('region') if body.get('region') else address.get('region')
    address['city'] = body.get('city') if body.get('city') else address.get('city')
    user_attributes['address'] = json.dumps(address)

    admin_update_user_attributes(user['email'], user_attributes)
    return {
        "statusCode": 200,
        "body": json.dumps(user)
    }
