import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
from role_validation import UserType, check_auth
from common import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    # FOR REFERENCE
    # # create a new session
    session = Session()
    jobAppId = event["pathParameters"]["id"]
    jobApp = session.query(JobApplication).get(jobAppId)

    # # commit and close session

    if jobApp == None:
        session.commit()
        session.close()
        return http_status.not_found()
    else:
        delete = session.query(JobApplication).filter(JobApplication.job_application_id == jobAppId).delete()
        session.commit()
        session.close()
        return http_status.success()