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

    
    # # create a new session
    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)

    
    if job != None: #if it was a valid jobid, and the job was found
        job.job_status = JobStatus.CLOSED
        
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Job Closed"
            })
        }
    else:
        return {
            "statusCode" : 404,
            "body" : json.dumps({
                "message": "ID not found"
            })
        }