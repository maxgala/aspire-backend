import sys
import json
import logging
import uuid
from datetime import datetime
from datetime import date
import time    

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from send_email import send_templated_email
import jwt
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
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    email = user['email']
    candidate_name = user["given_name"] + user["family_name"]

    session = Session()
    info = json.loads(event["body"])
    job_id = info.get('job_id')
    resumes = info.get('resumes')
    cover_letters = info.get('cover_letters')

    #Validate Body
    if not (job_id and resumes and cover_letters):
        return http_status.bad_request("missing parameter(s): 'job_id, resumes, cover_letters'")
    else:
        try:
            job_id = int(job_id)
        except ValueError:
            return http_status.bad_request("invalid parameter: 'job_id must be an integer'")

    job = session.query(Job).get(job_id)
    hiring_manager = job.posted_by
    if hiring_manager == email:
        return http_status.forbidden("Hiring manager cannot apply to the job")
    
    existing_job_application = session.query(JobApplication).filter(JobApplication.applicant_id == email).filter(JobApplication.job_id == job_id).all()
    if len(existing_job_application) > 0:
        return http_status.forbidden("You have already applied to this job")

    job_rs = JobApplication(
        job_id = job_id,
        applicant_id = email,
        job_application_status = JobApplicationStatus.SUBMIT,
        resumes = resumes,
        cover_letters = cover_letters
        )
    session.add(job_rs)
    session.commit()

    job_title = job.title
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = str(job.posted_by)

    # The send_email_templated function requires JSON Formatted Data with " strings "
    template_data = {
        "candidate_name": str(candidate_name),
        "job_title": str(job_title),
        "today": str(today)
    }
    template_data = json.dumps(template_data)
    recipients = [hiring_manager]
    send_templated_email(recipients, "CreateJobApplication", template_data)

    resp = row2dict(job_rs)
    session.close()

    return http_status.success(json.dumps(resp))