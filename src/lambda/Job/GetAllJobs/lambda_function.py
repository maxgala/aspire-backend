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
    page = event["queryStringParameters"].get('page') if event["queryStringParameters"] else None
    count = 2
    if page != None:
        jobs = session.query(Job).offset((int(page) * count) - count).limit(int(page) * count)
    else:
        jobs = session.query(Job).all()
    joblist = []
    for job in jobs:
        tags = []
        for tag in job.job_tags:
            tags.append(tag.name)
        job_json = {
            "title": job.title,
            "company":job.company,
	        "region":job.region,
	        "city":job.city,
            "country":job.country,
            "job_type": job.job_type.name,
	        "description":job.description,
	        "requirements":job.requirements,
	        "posted_by":job.posted_by,
	        "contact_email":job.contact_email,
	        "job_status":job.job_status.name,
	        "job_tags":tags,
	        "salary":int(job.salary),
	        "deadline":job.deadline.timestamp(),
            "created_on": job.created_on.timestamp(),
            "updated_on":job.updated_on.timestamp()
        }
        joblist.append(job_json)

    # # commit and close session
    
    session.close()

    return {
        "statusCode": 200,
        "body": {
            "jobs": json.dumps(joblist),
            "count": len(joblist)
        }
    }
