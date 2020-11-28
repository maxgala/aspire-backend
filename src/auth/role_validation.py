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
    if user_group not in allowedReadGroups:
        return False, None
    return True, user

def edit_auth(user, allowedWriteUser):
    success, user_group = get_group(user)
    if not success:
        return False
    if user_group != UserGroups.ADMIN and user['email'] != allowedWriteUser:
        return False
    return True

def get_group(user):
    user_groups = user.get('cognito:groups')
    if not user_groups:
        return False, None
    elif len(user_groups) > 1:
        return False, None
    if user_groups[0] not in UserGroups.__members__:
        return False, None
    return True, UserGroups[user_groups[0]]
