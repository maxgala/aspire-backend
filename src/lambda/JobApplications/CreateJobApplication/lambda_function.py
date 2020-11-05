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
from send_email import send_email
import jwt
from role_validation import UserGroups, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    email = user['email']
    candidate_name = user["given_name"] + user["family_name"]

    session = Session()
    info = json.loads(event["body"])
    job_rs = JobApplication(
        job_id = info["job_id"],
        applicant_id = email,
        job_application_status = "SUBMIT",
        resumes = info["resumes"],
        cover_letters = info["cover_letters"]
        )
    session.add(job_rs)
    session.commit()

    ##email hiring manager
    job = session.query(Job).get(info["job_id"])
    job_title = job.title
    job_date = job.created_on
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = job.posted_by
    job_date = datetime.fromtimestamp(job.created_on).strftime("%Y-%m-%d")
    subject = "[MAX Aspire] You have received a job application!"
    body = f"Salaam!\r\n\nWe would like to notify that {candidate_name} has applied to the job posting {job_title} on {today}. The aforementioned job was posted on MAX Aspire job board on {job_date}. Kindly login to your account to access the complete profile and application of the candidate. Once the application is reviewed the status can be changed to “Under Review”, “Invite for interview” or “Rejected”.\r\n\n Please note that the candidate is more responsive in the first 2 weeks of applying the job. If the job posting is unavailable for any reason kindly contact the support team ASAP.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
    # FIXME change sender email address
    hiring_manager = 'naba@poketapp.com'
    send_email(to_addresses=hiring_manager, subject=subject, body_text=body)

    resp = row2dict(job_rs)
    session.close()

    return {
        "statusCode": 201,
        "body": json.dumps(resp)
    }
