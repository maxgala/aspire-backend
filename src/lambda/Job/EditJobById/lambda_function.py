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
    info = json.loads(event["body"])
    print(info)

    
    if job != None: #if it was a valid jobid, and the job was found
        keys = info.keys()
        for key in keys:
            setattr(job,key,info[key])
        
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Row Updated"
            })
        }
    else:
        return {
            "statusCode" : 404,
            "body" : json.dumps({
                "message": "ID not found"
            })
        }

