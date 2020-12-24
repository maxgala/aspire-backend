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
    job_rs = JobApplication(
        job_id = info["job_id"],
        applicant_id = email,
        job_application_status = "SUBMIT",
        resumes = info["resumes"],
        cover_letters = info["cover_letters"]
        )
    session.add(job_rs)
    session.commit()

    job = session.query(Job).get(info["job_id"])
    job_title = job.title
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = job.posted_by
    subject = f"[MAX Aspire] {candidate_name} applied to your {job_title} job!"
    body = f"Salaam!\n\nWe would like to notify that {candidate_name} has applied to the job posting {job_title} on {today}.\n\nKindly login to your account to access the complete profile and application of the candidate. Once the application is reviewed the status can be changed to “Under Review”, “Invite for Interview” or “Rejected”.\n\nWe hope you get to read some amazing resume's in your review. Enjoy!\n\nBest regards,\nTeam MAX Aspire"
    send_email(to_addresses=hiring_manager, subject=subject, body_text=body)

    resp = row2dict(job_rs)
    session.close()

    return http_status.success(json.dumps(resp))
