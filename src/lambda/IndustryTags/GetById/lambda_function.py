import json
import logging

from industry_tag import IndustryTag
from base import Session, row2dict
from role_validation import UserType, check_auth
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID,
        UserType.FREE
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    industryTagId = event["pathParameters"].get("industryTagId") if event["pathParameters"] else None
    if not industryTagId:
        return http_status.bad_request("missing path parameter(s): 'industryTagId'")

    session = Session()
    industry_tag = session.query(IndustryTag).get(industryTagId.lower())
    session.close()
    if not industry_tag:
        return http_status.not_found()

    return http_status.success(json.dumps(
            row2dict(industry_tag)
        ))
