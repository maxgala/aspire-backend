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
    jobApp = session.query(JobApplication).get(jobAppId)
    
    print(jobApp)

    # # commit and close session
    
    session.close()

    if jobApp != None:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "job id": jobApp.job_id,
                "applicant id": jobApp.applicant_id,
                "documents": jobApp.documents,
                "job application status": jobApp.job_application_status.name,
                "created_on": jobApp.created_on.timestamp(),
                "updated_on":jobApp.updated_on.timestamp()
            })
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Record with that ID was not found"
            })
        }
    