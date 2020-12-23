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
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    # email = user['email']
    # candidate_name = user["given_name"] + user["family_name"]
    email = "tayyaabtanveer@gmail.com"
    candidate_name= "dfadsf"

    session = Session()
    info = json.loads(event["body"])
    complete = True

    job_id = info.get('job_id')
    resumes = info.get('resumes')
    cover_letters = info.get('cover_letters')

    #Validate Body
    if not (job_id and resumes and cover_letters):
        complete = False
    else:
        try:
            job_id = int(job_id)
        except ValueError:
            complete = False

    if not complete:
        return {
            "statusCode": 400,
            "headers": {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                    'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    else:
        job_rs = JobApplication(
            job_id = job_id,
            applicant_id = email,
            job_application_status = "SUBMIT",
            resumes = resumes,
            cover_letters = cover_letters
            )
        session.add(job_rs)
        session.commit()

        ##email hiring manager
        job = session.query(Job).get(info["job_id"])
        job_title = job.title
        today = datetime.today().strftime("%Y-%m-%d")
        hiring_manager = job.posted_by
        subject = "[MAX Aspire] You have received a job application!"
        body = f"Salaam!\r\n\nWe would like to notify that {candidate_name} has applied to the job posting {job_title} on {today}. Kindly login to your account to access the complete profile and application of the candidate. Once the application is reviewed the status can be changed to “Under Review”, “Invite for interview” or “Rejected”.\r\n\n Please note that the candidate is more responsive in the first 2 weeks of applying the job. If the job posting is unavailable for any reason kindly contact the support team ASAP.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
        # send_email(to_addresses=hiring_manager, subject=subject, body_text=body)

        resp = row2dict(job_rs)
        session.close()

        return {
            "statusCode": 201,
            "body": json.dumps(resp),
            "headers": {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                    'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                }
        }

