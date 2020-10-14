import json
import logging
import boto3

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    response = client.list_users(
        UserPoolId='us-east-1_T02rYkaXy',
        Filter="status = 'Disabled'"
    )

    raw_users = response['Users']
    print(raw_users)

    users = []
    for raw_user in raw_users:
        raw_attributes = raw_user['Attributes']
        attributes = {}
        for attr in raw_attributes:
            attributes[attr['Name']] = attr['Value']
            
        user = {}
        user['username'] = raw_user['Username']
        user['attributes'] = attributes
        user['status'] = raw_user['UserStatus']
        user['enabled'] = raw_user['Enabled']
        users.append(user)

    return {
        "statusCode": 200,
        "body": json.dumps({
            'users': users,
        }),
    }
