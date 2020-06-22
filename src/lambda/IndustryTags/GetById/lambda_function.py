import json
import logging
import enum
from datetime import datetime

from industry_tag import IndustryTag
from base import Session, engine, Base

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        key = column.name
        val = getattr(row, column.name)
        if isinstance(val, datetime):
            val = val.timestamp()
        elif isinstance(val, enum.Enum):
            val = val.name
        elif isinstance(val, list):
            if isinstance(val[0], enum.Enum):
                val = [v.name for v in val]
        d[key] = val
    return d


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
    industry_tag = session.query(IndustryTag).get(industryTagId)
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
        "body": json.dumps({
            "industry_tag": row2dict(industry_tag)
        })
    }
