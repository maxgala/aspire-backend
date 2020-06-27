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
    jobAppId = event["pathParameters"]["jobAppId"]
    records = session.query(JobApplication).filter(JobApplication.job_application_id == jobAppId).first()

    # # commit and close session
    session.commit()
    session.close()

    if records == None:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Record with that ID was not found"
            })
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Row deleted"
            })
        }
