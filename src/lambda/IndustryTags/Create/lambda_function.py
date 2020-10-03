import json
import logging

from industry_tag import IndustryTag
from base import Session
from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.FREE,
        UserGroups.PAID
    ]
    err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    if err:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": group_response
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
