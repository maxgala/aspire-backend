import enum
import jwt


class UserType(enum.Enum):
    ADMIN = 1
    MENTOR = 2
    PAID = 3
    FREE = 4


def check_auth(auth_header: str, allowedUserTypes: list):
    id_token = auth_header.split('Bearer ')[1]
    if not id_token:
        return False

    user = jwt.decode(id_token, verify=False)
    success, user_type = validate_user_type(user)
    if not success:
        return False, None
    if user_type not in allowedUserTypes:
        return False, None
    return True, user

def edit_auth(user: dict, allowedUserType: str):
    success, user_type = validate_user_type(user)
    if not success:
        return False
    if user_type != UserType.ADMIN and user['email'] != allowedUserType:
        return False
    return True

def validate_user_type(user: dict):
    user_type = user.get('custom:user_type')
    if not user_type:
        return False, None
    if user_type not in UserType.__members__:
        return False, None
    return True, UserType[user_type]
