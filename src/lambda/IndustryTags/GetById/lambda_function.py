import json
import logging

from industry_tag import IndustryTag
from base import Session, row2dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
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
