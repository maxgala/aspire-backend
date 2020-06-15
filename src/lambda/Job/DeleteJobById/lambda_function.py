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
    
    # looking for job applications associated with the jobID
    records = session.query(JobApplication).filter(JobApplication.job_id == jobId).first()
    print(records)
    
    if records != None:
        output = "Row has foreign key reference in Job Applications Table"
    else:
        output = "Row Deleted"
        count = session.query(Job).filter(Job.job_id == jobId).delete()
        
    # # commit and close session
    session.commit()
    session.close()

    if records == None and count == 0 :
         return {
            "statusCode": 404,
            "body": "ID not found"
        }
    else:    
        return {
            "statusCode": 200,
            "body": json.dumps(output)
        }
