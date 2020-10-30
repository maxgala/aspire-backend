import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.FREE,
        UserGroups.PAID
    ]
    err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    if err:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": group_response
            })
        }

    # FOR REFERENCE
    # # create a new session
    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    print(job)
    
    if job != None:
        print(job.job_applications)
        job_apps_id = []
        #import pdb; pdb.set_trace()
        for app in job.job_applications:
            job_apps_id.append(app.job_application_id)
        jobdict = row2dict(job)
        jobdict['job_applications'] = job_apps_id
        session.close()
        return {
            "statusCode": 200,
            "body": json.dumps(jobdict)
        }
        # # commit and close session
        
    else:
        session.close()
        return {
            "statusCode" : 404,
            "body" : json.dumps({
                "message": "ID not found"
            })
        }    
