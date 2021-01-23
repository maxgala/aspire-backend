import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserType, check_auth
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID,
        UserType.FREE
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    
    if job != None:
        job_apps_id = []
        for app in job.job_applications:
            job_apps_id.append(app.job_application_id)
        jobdict = row2dict(job)
        jobdict['job_applications'] = job_apps_id
        session.close()
        return http_status.success(json.dumps(jobdict))
    else:
        session.close()
        return http_status.not_found()