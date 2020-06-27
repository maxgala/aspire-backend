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
    # applicantId = event["pathParameters"]["applicantId"]
    jobId = event["queryStringParameters"].get('jobId') if event["queryStringParameters"] else None
    applicantId = event["queryStringParameters"].get('userId') if event["queryStringParameters"] else None
    IdFound = True

    if applicantId != None:
        jobApps = session.query(JobApplication).filter(JobApplication.applicant_id == applicantId).all()
    elif jobId != None:
        jobApps = session.query(JobApplication).filter(JobApplication.job_id == jobId).all()
    else:
        jobApps = session.query(JobApplication).all()
        IdFound = False
    
    # # commit and close session
    
    session.close()

    jobAppsList = []

    for jobApp in jobApps:
        jobApp_json = {
            "job id": jobApp.job_id,
            "applicant id": jobApp.applicant_id,
            "documents": jobApp.documents,
            "job application status": jobApp.job_application_status.name,
            "created_on": jobApp.created_on.timestamp(),
            "updated_on":jobApp.updated_on.timestamp()
        }
        jobAppsList.append(jobApp_json)

    if jobAppsList:
        return {
            "statusCode": 200,
            "body": json.dumps(jobAppsList)
        }

    elif IdFound:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Record with that ID was not found"
            })
        }

    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Table is empty"
            })
        }
            
    