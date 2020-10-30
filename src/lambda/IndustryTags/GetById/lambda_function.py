import json
import logging

from industry_tag import IndustryTag
from base import Session, row2dict
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
    success, user = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    industryTagId = event["pathParameters"].get("industryTagId") if event["pathParameters"] else None
    if not industryTagId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'industryTagId'"
            })
        }

    session = Session()
    industry_tag = session.query(IndustryTag).get(industryTagId.lower())
    session.close()
    if not industry_tag:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "industry tag with id '{}' not found".format(industryTagId)
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(industry_tag)
        )
    }
