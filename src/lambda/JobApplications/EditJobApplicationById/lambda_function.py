import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
from role_validation import UserType, check_auth
import http_status

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

    session = Session()
    info = json.loads(event["body"])
    jobAppId = event["pathParameters"]["id"]
    jobApp = session.query(JobApplication).get(jobAppId)

    if jobApp != None:
        keys = info.keys()
        for key in keys:
            setattr(jobApp,key,info[key])

        session.commit()
        session.close()

        return http_status.success(json.dumps(info))
    else:
        return http_status.not_found()