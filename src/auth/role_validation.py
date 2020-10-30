import enum
import jwt

class UserGroups(enum.Enum):
    ADMIN = 1
    MENTOR = 2
    FREE = 3
    PAID = 4

def check_auth(auth_header, allowedReadGroups):
    id_token = auth_header.split('Bearer ')[1]
    if not id_token:
        return False

    user = jwt.decode(id_token, verify=False)
    success, user_group = get_group(user)
    if not success:
        return False, None

    success = validate_user(user_group, allowedReadGroups)
    if not success:
        return False, None
    return True, user

def edit_auth(user, allowedWriteUser):
    success, user_group = get_group(user)
    if user_group != UserGroups.ADMIN and user['email'] != allowedWriteUser:
        return False
    return True

def validate_user(user_group, allowedGroups):
    if user_group not in UserGroups.__members__ or \
        UserGroups[user_group] not in allowedGroups:
        return False
    return True

def get_group(user):
    user_groups = user.get('cognito:groups')
    if not user_groups:
        return False, None
    elif len(user_groups) > 1:
        return False, None
    return True, user_groups[0]
