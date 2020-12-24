import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
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

    session = Session()

    info = json.loads(event["body"])

    tags = []
    for tag in info["job_tags"]:
        tags.append(JobTags[tag])

    job_title = info["title"]

    deadline = datetime.fromtimestamp(info["deadline"]).replace(hour=0, minute=0,second=0, microsecond=0)

    Job_row = Job(title=job_title, company=info["company"],
                    region=info["region"], city=info["city"], country=info["country"], job_type=JobType[info["job_type"]],
                    description=info["description"], requirements=info["requirements"], posted_by=info["posted_by"],
                    poster_family_name = info["poster_family_name"], poster_given_name = info["poster_given_name"],
                    job_status="UNDER_REVIEW",job_tags=tags, salary=info["salary"], deadline = deadline, can_contact = info["can_contact"])

    session.add(Job_row)        
    session.commit()
    res = row2dict(Job_row)
    session.close()

    ##email hiring manager
    job_title = info["title"]
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = info["posted_by"]   
    subject = f"[MAX Aspire] Your {job_title} job is under review"
    body = f"Salaam!\n\nThank you for choosing MAX Aspire as your entrusted partner. I am delighted to confirm that we have received your job posting {job_title} on {today}.\n\nYour Job Posting will be reviewed and if approved, will go LIVE within 36 hours.\n\nYou will be notified by email as individuals apply for the position.\n\nThank you.\n\nKind Regards,\nTeam MAX Aspire"
    send_email(to_addresses=hiring_manager, subject=subject, body_text=body)

    return http_status.success(json.dumps(res))