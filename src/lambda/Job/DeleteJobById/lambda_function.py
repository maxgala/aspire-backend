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
        output = "Row has foreign key reference in Job Applications Table"
    else: # when there are no job applications associated to a job, and the job can be deleted
        output = "Row Deleted"
        session.query(Job).filter(Job.job_id == jobId).delete()
        
    # # commit and close session
    session.commit()
    session.close()
   
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": output
        })
    }
