import logging
import boto3
import os
from dotenv import load_dotenv

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

client = boto3.client('cognito-idp')
userPoolId = os.getenv('COGNITO_POOL_ID')

def get_users(filter_: tuple=('status', 'Enabled'), attributes_filter: list=None, user_type=None):
    if user_type and not isinstance(user_type, list):
        user_type = [user_type]

    params = {
        "UserPoolId": userPoolId,
        "Filter": "{} = '{}'".format(filter_[0], filter_[1])
    }
    if attributes_filter:
        params["AttributesToGet"] = attributes_filter

    response = client.list_users(**params)
    raw_users =  response['Users']
    pagination_token = response.get('PaginationToken')
    while pagination_token != None:
        params['PaginationToken'] = pagination_token
        response = client.list_users(**params)
        raw_users += response['Users']
        pagination_token = response.get('PaginationToken')

    users = {}
    for raw_user in raw_users:
        raw_attributes = raw_user['Attributes']
        attributes = {}
        for attr in raw_attributes:
            attributes[attr['Name']] = attr['Value']

        # filter by user_type
        if user_type and attributes['custom:user_type'] not in user_type:
            continue
        
        try:
            email = attributes['email']
        except:
            logging.error('cannot find email')
            logging.error(attributes)
            email = raw_user['Username']

        user = {}
        user['username'] = raw_user['Username']
        user['attributes'] = attributes
        user['status'] = raw_user['UserStatus']
        user['enabled'] = raw_user['Enabled']
        users[email] = user
    return users[list(users.keys())[0]] if len(users.keys()) == 1 else users, len(users.keys())

def admin_update_user_attributes(email, attributes):
    response = client.admin_update_user_attributes(
        UserPoolId=userPoolId,
        Username=email,
        UserAttributes=[
            {'Name': key, 'Value': val} for key, val in attributes.items()
        ]
    )
    # logger.info(response)

def admin_update_credits(email, value):
    user, _ = get_users(filter_=('email', email), attributes_filter=['custom:credits'])
    user_credits = int(user['attributes']['custom:credits'])

    response = client.admin_update_user_attributes(
        UserPoolId=userPoolId,
        Username=email,
        UserAttributes=[
            {
                'Name': 'custom:credits',
                'Value': str(user_credits + value)
            }
        ]
    )
    # logger.info(response)

def admin_update_declared_chats_frequency(email, value):
    user, _ = get_users(filter_=('email', email), attributes_filter=['custom:declared_chats_freq'])
    declared_chats_frequency = int(user['attributes']['custom:declared_chats_freq'])

    response = client.admin_update_user_attributes(
        UserPoolId=userPoolId,
        Username=email,
        UserAttributes=[
            {
                'Name': 'custom:declared_chats_freq',
                'Value': str(declared_chats_frequency + value)
            }
        ]
    )
    # logger.info(response)

def admin_update_remaining_chats_frequency(email, value):
    user, _ = get_users(filter_=('email', email), attributes_filter=['custom:remaining_chats_freq'])
    remaining_chats_frequency = int(user['attributes']['custom:remaining_chats_freq'])

    response = client.admin_update_user_attributes(
        UserPoolId=userPoolId,
        Username=email,
        UserAttributes=[
            {
                'Name': 'custom:remaining_chats_freq',
                'Value': str(remaining_chats_frequency + value)
            }
        ]
    )
    # logger.info(response)

def admin_disable_user(email):
    response = client.admin_disable_user(
        UserPoolId=userPoolId,
        Username=email
    )
    # logger.info(response)

def admin_enable_user(email):
    response = client.admin_enable_user(
        UserPoolId=userPoolId,
        Username=email
    )
    # logger.info(response)
