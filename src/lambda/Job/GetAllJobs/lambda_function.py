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
    
    jobs = session.query(Job).all()
    joblist = []
    for job in jobs:
        x = {
            "title": job.title,
            "company":job.company,
	        "province":job.province,
	        "city":job.city,
            "num_applicants":job.num_applicants,
            "job_type": job.job_type.name,
	        "description":job.description,
	        "requirements":job.requirements,
	        "posted_by":job.posted_by,
	        "contact_email":job.contact_email,
	        "job_status":job.job_status.name,
	        "job_tags":job.job_tags.name,
	        "salary":int(job.salary),
	        "deadline":job.deadline.strftime("%m/%d/%Y"),
            "created_on": job.created_on.strftime("%m/%d/%Y"),
            "updated_on":job.updated_on.strftime("%m/%d/%Y")
        }
        joblist.append(x)

    # # commit and close session
    
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps(joblist)
    }
