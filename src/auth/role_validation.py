import enum
import boto3

class UserGroups(enum.Enum):
    ADMIN = 1
    MENTOR = 2
    FREE = 3
    PAID = 4

client = boto3.client('sts')


def assume_role(eventAuthorizerClaims, roleSessionName):
    role = eventAuthorizerClaims.get('cognito:roles', '')
    if not role:
        return True, "role not specified"
    elif len(role.split(',')) > 1:
        return True, "multiple roles specified"

    response = client.assume_role(RoleArn=role, RoleSessionName=roleSessionName)
    return False, response

def validate_group(eventAuthorizerClaims, allowedGroups):
    err, group_name = get_group(eventAuthorizerClaims)
    if err:
        return err, group_name

    try:
        group = UserGroups[group_name]
        if group not in allowedGroups:
            return True, "unauthorized"

        return False, "authorized"
    except KeyError:
        return True, "unauthorized"

def get_group(eventAuthorizerClaims):
    group = eventAuthorizerClaims.get('cognito:groups', '')
    if not group:
        return True, "user group not specified"
    elif len(group.split(',')) > 1:
        return True, "multiple user groups specified"

    return False, group
