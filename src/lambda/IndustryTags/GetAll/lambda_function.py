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
    body = event["body"]
    filter_ = event["queryStringParameters"].get("filter", "") if event["queryStringParameters"] else ""

    session = Session()
    industry_tags = session.query(IndustryTag).filter(IndustryTag.tag.ilike("{}%".format(filter_))).all()
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "industry_tags": [row2dict(r) for r in industry_tags],
            "count": len(industry_tags)
        })
    }
