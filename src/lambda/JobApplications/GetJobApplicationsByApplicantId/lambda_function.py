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
    applicantId = event["pathParameters"]["applicantId"]
    jobApps = session.query(JobApplication).filter(JobApplication.applicant_id == applicantId).all()
    
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

    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Record with that Applicant ID was not found"
            })
        }
    