import json
import logging

from industry_tag import IndustryTag
from base import Session
from role_validation import UserType, check_auth
from common import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [UserType.ADMIN]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    industryTagId = event["pathParameters"].get("industryTagId") if event["pathParameters"] else None
    if not industryTagId:
        return http_status.bad_request("missing path parameter(s): 'industryTagId'")

    session = Session()
    industry_tag = session.query(IndustryTag).get(industryTagId.lower())
    if not industry_tag:
        session.close()
        return http_status.not_found()

    session.delete(industry_tag)
    session.commit()
    session.close()

    return http_status.success()