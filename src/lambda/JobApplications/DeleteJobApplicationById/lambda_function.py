import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
from role_validation import UserGroups, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    # FOR REFERENCE
    # # create a new session
    session = Session()
    jobAppId = event["pathParameters"]["id"]
    jobApp = session.query(JobApplication).get(jobAppId)

    # # commit and close session

    if jobApp == None:
        session.commit()
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Record with that ID was not found"
            })
        }
    else:
        delete = session.query(JobApplication).filter(JobApplication.job_application_id == jobAppId).delete()
        session.commit()
        session.close()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Row deleted"
            })
        }
