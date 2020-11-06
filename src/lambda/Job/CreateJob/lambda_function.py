import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserGroups, check_auth
from send_email import send_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps
                "errorMessage": "unauthorized"
            })
        }

    session = Session()

    info = json.loads(event["body"])

    tags = []
    for tag in info["job_tags"]:
        tags.append(JobTags[tag])

    Job_row = Job(title=info["title"], company=info["company"],
                    region=info["region"], city=info["city"], country=info["country"], job_type=JobType[info["job_type"]],
                    description=info["description"], requirements=info["requirements"], posted_by=info["posted_by"],
                    poster_family_name = info["poster_family_name"], poster_given_name = info["poster_given_name"],
                    job_status=JobStatus["UNDER_REVIEW"],job_tags=tags, salary=info["salary"], deadline = info["deadline"])

    session.add(Job_row)        
    session.commit()
    session.close()

    ##email hiring manager
    job_title = info["title"]
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = info["posted_by"]    
    subject = "[MAX Aspire] The job you posted is under review"
    body = f"Salaam!\r\n\nThank you for choosing MAX Aspire as your entrusted partner. I am delighted to confirm that we have received your job posting {job_title} on {today}. A member of our team is currently reviewing the job posting to make sure it meets all the necessary requirements.\r\n\nOnce approved, you will be notified via email/member portal. Subsequently you will be notified if any additional information is required. Kindly bear with us 2-3 days before the job is approved and posted on MAX Aspire Job Board. Thank you.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
    send_email(to_addresses=hiring_manager, subject=subject, body_text=body)

    return {
        "statusCode": 201,
        "body": json.dumps(
            row2dict(Job_row)
        )
    }
