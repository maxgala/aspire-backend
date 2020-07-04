import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    info = json.loads(event["body"])
    jobAppId = event["pathParameters"]["jobAppId"]
    jobApp = session.query(JobApplication).get(jobAppId)

    if jobApp != None:
        keys = info.keys()
        for key in keys:
            setattr(jobApp,key,info[key])

        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps(info),
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Record with that ID was not found"
            })
        }
    