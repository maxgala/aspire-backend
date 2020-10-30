import json
import logging

from industry_tag import IndustryTag
from base import Session
from role_validation import UserGroups, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID,
        UserGroups.FREE
    ]
    success, _ = read_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    body = json.loads(event["body"])
    tag = body.get("tag") if body else None

    if not tag:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'tag'"
            })
        }

    IndustryTag_new = IndustryTag(tag=tag.lower())

    session = Session()
    session.add(IndustryTag_new)
    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
