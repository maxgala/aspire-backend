import logging
import boto3

client = boto3.client('cognito-idp')
userPoolId = 'us-east-1_T02rYkaXy'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_user_attributes(email, attributes):
    response = client.list_users(
        UserPoolId=userPoolId,
        AttributesToGet=attributes,
        Filter = 'email="{}"'.format(email)
    )
    logger.info(response)

    raw_attributes = response['Users'][0]['Attributes']
    attributes = {}
    for attr in raw_attributes:
        attributes[attr['Name']] = attr['Value']
    return attributes

def admin_update_credits(email, value):
    attributes = get_user_attributes(email, attributes=['custom:credits'])
    user_credits = attributes['custom:credits']

    response = client.admin_update_user_attributes(
        UserPoolId=userPoolId,
        Username=email,
        UserAttributes=[
            {
                'Name': 'custom:credits',
                'Value': user_credits + value
            }
        ]
    )
    logger.info(response)

def admin_update_remaining_chats_frequency(email, value):
    attributes = get_user_attributes(email, attributes=['custom:remaining_chats_frequency'])
    remaining_chats_frequency = attributes['custom:remaining_chats_frequency']

    response = client.admin_update_user_attributes(
        UserPoolId=userPoolId,
        Username=email,
        UserAttributes=[
            {
                'Name': 'custom:remaining_chats_frequency',
                'Value': remaining_chats_frequency + value
            }
        ]
    )
    logger.info(response)
