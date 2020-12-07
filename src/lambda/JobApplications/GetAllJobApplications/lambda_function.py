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
        UserType.PAID,
        UserType.FREE
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
    applicantId = ""
    jobId = ""

    if event["queryStringParameters"] != None:
        if event["queryStringParameters"].get('jobId') != None:
            jobId = event["queryStringParameters"].get('jobId') 
        if event["queryStringParameters"].get('userId') != None:
            applicantId = event["queryStringParameters"].get('userId')

        #Checks to see if any keys passed in are empty, and then performs one search accordingly.
    if (applicantId != None and  applicantId != "" and jobId != None and jobId != "" ):
        jobApps = session.query(JobApplication).filter(JobApplication.applicant_id == applicantId, JobApplication.job_id == jobId).all()
    elif (jobId != None and jobId != ""):
        jobApps = session.query(JobApplication).filter(JobApplication.job_id == jobId).all()
    elif (applicantId != None and applicantId != ""):
        jobApps = session.query(JobApplication).filter(JobApplication.applicant_id == applicantId).all()        
    else:
        jobApps = session.query(JobApplication).all()
    
    # # commit and close session
    
    session.close()

    jobAppsList = []
    
    for jobApp in jobApps:
        jobApp_json = {
            "job_application_id": jobApp.job_application_id,
            "job_id": jobApp.job_id,
            "applicant_id": jobApp.applicant_id,
            "resumes": jobApp.resumes,
            "cover_letters": jobApp.cover_letters,
            "job_application_status": jobApp.job_application_status.name,
            "created_on": jobApp.created_on.timestamp(),
            "updated_on":jobApp.updated_on.timestamp()
        }
        jobAppsList.append(jobApp_json)
    return {
        "statusCode": 200,
        "body": json.dumps(jobAppsList),
        "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
    }