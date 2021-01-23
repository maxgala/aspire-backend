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

    search = event["queryStringParameters"].get("search", "") if event["queryStringParameters"] else ""
    fuzzy = event["queryStringParameters"].get("fuzzy", "") if event["queryStringParameters"] else ""

    session = Session()
    if fuzzy.lower() == "true":
        industry_tags = session.query(IndustryTag).filter(IndustryTag.tag.ilike("%{}%".format(search))).all()
    else:
        industry_tags = session.query(IndustryTag).filter(IndustryTag.tag.ilike("{}%".format(search))).all()
    session.close()

    return http_status.success(json.dumps({
            "industry_tags": [row2dict(r) for r in industry_tags],
            "count": len(industry_tags)
        }))
