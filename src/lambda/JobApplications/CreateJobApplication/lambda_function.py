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
    info = json.loads(event["body"])
   

   ## Need to add user lookup which is connected to AWS Cognito

    Job_application_row = JobApplication(
        job_id = info["job_id"],
        applicant_id = info["applicant_id"],
        job_application_status = JobApplicationStatus[info["status"]],
        documents = info["documents"]
        )


    # # persists data
    session.add(Job_application_row)

    # # commit and close session
    session.commit()
    session.close()

#change to info

    return {
        "statusCode": 200,
        "body": json.dumps({
         "Created": info
        }),
    }
    