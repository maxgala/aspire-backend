import enum

class UserGroups(enum.Enum):
    ADMIN = 1
    MENTOR = 2
    FREE = 3
    PAID = 4

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
        return True, "user doesn't belong to a group"
    elif len(group.split(',')) > 1:
        return True, "user belongs to multiple groups"

    return False, group
