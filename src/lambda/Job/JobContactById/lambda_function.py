import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
import jwt
import boto3
from role_validation import UserType, check_auth
import http_status

client = boto3.client('cognito-idp')

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

    access_token = event['headers']['X-Aspire-Access-Token']

    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    
    if job == None:
        return http_status.not_found()
    
    credit = int(user['custom:credits'])
    email = user['email']

    if job.can_contact:
        applied = False
        for job_app in job.job_applications:
            if job_app.applicant_id == email:
                applied = True
        if not applied:
            return http_status.forbidden("You need to apply to the job before requesting contact-information")

        if job.people_contacted >= 4:
            return http_status.forbidden("Limit of contact information requests has been exceeded")

        if int(credit) < 5:
            return http_status.forbidden("You do not have enough credits to request contact information")
        response = client.update_user_attributes(
            UserAttributes=[
                {
                    'Name': 'custom:credits',
                    'Value': str(int(credit) - 5) #deducting credits for requesting contact_info
                },
            ],
            AccessToken=access_token
        )
        job.people_contacted = job.people_contacted + 1
        session.commit()
        return http_status.success(json.dumps({
                "contact_details": {
                        "email" : job.posted_by,
                        "given_name" : job.poster_given_name,
                        "family_name" : job.poster_family_name
                    }   
            }))
    else:
        return http_status.success(json.dumps({
                    "message": "Hiring manager does not want to be contacted"
                }))