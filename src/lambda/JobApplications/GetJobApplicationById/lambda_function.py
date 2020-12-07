import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserType, check_auth


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # check authorization
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
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    # FOR REFERENCE
    # # create a new session
    session = Session()
    jobAppId = event["pathParameters"]["id"]
    jobApp = session.query(JobApplication).get(jobAppId)
    
    # # commit and close session
    
    session.close()

    if jobApp != None:
        jobAppDict = row2dict(jobApp)
        return {
            "statusCode": 200,
            "body": json.dumps(jobAppDict),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Not Found"
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }
    