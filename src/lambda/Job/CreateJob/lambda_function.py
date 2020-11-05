import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
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
        UserGroups.PAID,
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
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
                    job_status=JobStatus[info["job_status"]] if "job_status" in info else "OPEN",job_tags=tags, salary=info["salary"], deadline = info["deadline"])

    session.add(Job_row)        
    session.commit()
    job_dict = row2dict(Job_row)
    session.close()

    ##email hiring manager
    job_title = info["title"]
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = info["posted_by"]    
    subject = "[MAX Aspire] Your job is now posted!"
    body = f"Salaam!\r\n\nWe are delighted to confirm that the job posting {job_title} is successfully posted on MAX Aspire job board on {today}. You will frequently be notified about the job applications as and when received. Keep an eye on your member portal/email.\r\n\nWe appreciate you putting your trust in MAX Aspire. We wish you luck in hiring the best possible candidate form our talented pool of aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
    send_email(to_addresses=hiring_manager, subject=subject, body_text=body)
    
    return {
        "statusCode": 201,
        "body": job_dict
    }
    