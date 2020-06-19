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
    session.query(JobApplication).filter(JobApplication.job_application_id == jobAppId).delete()
    

    # # commit and close session
    session.commit()
    session.close()

    return {
        "statusCode": 200,
        "body": "Row Deleted"
    }
