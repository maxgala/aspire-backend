import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    page = None
    user_id = None
    status = None
    page_size = 3
    if event["queryStringParameters"]:
        page = event["queryStringParameters"].get('page') #returns None if 'page' not in dict
        user_id = event["queryStringParameters"].get('user_id')
        status = event["queryStringParameters"].get('status')
        page_size = int(event["queryStringParameters"].get('page_size',3))

    print(status)
    print(user_id)
    print(page)
    print(page_size)
    jobs = session.query(Job)
    if user_id != None:
        jobs = jobs.filter(Job.posted_by == user_id)
    if status != None:
        jobs = jobs.filter(Job.job_status == status)
    if page != None:
        jobs = jobs.offset((int(page) * page_size) - page_size).limit(page_size)
   
    joblist = []
    for job in jobs:
        job_apps_id = []
        for app in job.job_applications:
            job_apps_id.append(app.job_application_id)
        jobdict = row2dict(job)
        jobdict['job_applications'] = job_apps_id
        joblist.append(jobdict)
        

    # # commit and close session
    
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "jobs": joblist,
            "count": len(joblist)
        })
    }
