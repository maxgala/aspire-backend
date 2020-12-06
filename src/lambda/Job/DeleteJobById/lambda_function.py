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

    # FOR REFERENCE
    # # create a new session
    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    if job == None:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID not found"
            })
        }
    if len(job.job_applications) != 0: # when there are job applications associated to a job
        return {
            "statusCode": 409,
            "body": json.dumps({
                "message": "Row has foreign key reference in Job Applications Table"
            })
        }

    session.query(Job).filter(Job.job_id == jobId).delete()
        
    # # commit and close session
    session.commit()
    session.close()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Row deleted"
        })
    }