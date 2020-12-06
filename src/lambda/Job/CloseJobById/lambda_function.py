import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
from role_validation import UserType, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }
    
    # # create a new session
    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)

    
    if job != None:
        job.job_status = JobStatus.CLOSED
        
        session.commit()
        session.close()

        return {
            "statusCode": 200
        }
    else:
        session.close()
        return {
            "statusCode" : 404,
            "body" : json.dumps({
                "message": "Not Found"
            })
        }