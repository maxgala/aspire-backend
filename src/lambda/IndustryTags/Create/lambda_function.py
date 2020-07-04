import sys
import json
import logging
import uuid

from industry_tag import IndustryTag
from base import Session, engine, Base

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    body = json.loads(event["body"])
    new_tag = body.get("tag") if body else None

    if not new_tag:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'tag'"
            })
        }

    Job_row = IndustryTag(tag=new_tag.lower())

    session = Session()
    session.add(Job_row)
    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
