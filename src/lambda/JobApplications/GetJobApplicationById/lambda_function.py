import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserType, check_auth
from common import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID,
        UserType.FREE
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    session = Session()
    jobAppId = event["pathParameters"]["id"]
    jobApp = session.query(JobApplication).get(jobAppId)
        
    session.close()

    if jobApp != None:
        jobAppDict = row2dict(jobApp)
        return http_status.success(json.dumps(jobAppDict))
    else:
        return http_status.not_found()