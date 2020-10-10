import sys
import json
import logging
import uuid
from datetime import datetime
from datetime import date
import time    


# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from send_email import send_email_Jobs, Identity
import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):    
    id_token = (event['headers']['Authorization']).split('Bearer ')[1]
    user = jwt.decode(id_token, verify=False)

    email = user['email']
    user_type = user['custom:user_type']
    mem_type = user['custom:membership_type']

    session = Session()

    if user_type == 'Mentor' or (user_type == 'Mentee' and mem_type == 'premium'):

        info = json.loads(event["body"])

        Job_application_row = JobApplication(
            job_id = info["job_id"],
            applicant_id = info["email"],
            job_application_status = JobApplicationStatus[info["job_application_status"]],
            resumes = info["resumes"],
            cover_letters = info["cover_letters"]
            )

        session.add(Job_application_row)
        session.commit()
        session.close()

        ##email hiring manager
        job = session.query(Job).get(info["job_id"])
        hiring_manager = job.posted_by
        JobName = job.title
        JobDateInt = job.created_on
        JobDate = datetime.fromtimestamp(JobDateInt).strftime("%Y-%m-%d")
        rec1= Identity("Recipient name", hiring_manager)
        recipients = [rec1]
        subject = "Hello world"
        body = "lorem ipsum dolor sit amet"
        sender = Identity("Sender name", email)
        send_email_Jobs(sender, recipients, subject, body, JobName, JobDate)

        return {
            "statusCode": 201,
            "body": json.dumps(row2dict(Job_application_row))
        }

    else:
        return {
            "statusCode": 426,
            "body": json.dumps({
                "message": "Insufficient privileges to post a job application"
            }),
        }
