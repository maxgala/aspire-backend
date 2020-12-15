import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
from role_validation import UserType, check_auth
from send_email import send_email
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

    # # create a new session
    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    info = json.loads(event["body"])
    
    if job != None: #if it was a valid jobid, and the job was found
        keys = info.keys()
        for key in keys:
            setattr(job,key,info[key])
        
        session.commit()
        session.close()

        if "job_status" in keys and info["job_status"] is "ACTIVE":
            job_title = job.title
            today = datetime.today().strftime("%Y-%m-%d")
            hiring_manager = job.posted_by    
            subject = "[MAX Aspire] Your job is now active!"
            body = f"Salaam!\r\n\nWe are delighted to confirm that the job posting {job_title} is successfully posted on MAX Aspire job board on {today}. You will frequently be notified about the job applications as and when received. Keep an eye on your member portal/email.\r\n\nWe appreciate you putting your trust in MAX Aspire. We wish you luck in hiring the best possible candidate form our talented pool of aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
            send_email(to_addresses=hiring_manager, subject=subject, body_text=body)

        return http_status.success()
    else:
        return http_status.not_found()