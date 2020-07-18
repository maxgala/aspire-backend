import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
import boto3

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    
    try:
        access_token = (event['headers']['Authorization']).replace('Bearer ', '')
    except:
        return {
        "statusCode": 401,
        "body": json.dumps({
            "message": "Authorization header is expected"
        }),
    }

    get_user_response =client.get_user(
            AccessToken=access_token
        )
    user_att = get_user_response['UserAttributes']
    mem_type = ''
    for att in user_att:
        if att['Name'] == 'custom:user_type':
            user_type = att['Value']
        elif att['Name'] == 'email':
            email = att['Value']            
        try:
            if att['Name'] == 'custom:membership_type':
                mem_type = att['Value']
        except:
            pass

    if user_type == 'Mentor' or (user_type == 'Mentee' and mem_type == 'premium'):

        info = json.loads(event["body"])

        Job_application_row = JobApplication(
            job_id = info["job_id"],
            applicant_id = email,
            job_application_status = JobApplicationStatus[info["job_application_status"]],
            resumes = info["resumes"],
            cover_letters = info["cover_letters"]
            )
       
        # # persists data
        session.add(Job_application_row)

        # # commit and close session
        session.commit()
        session.close()

    #change to info

        return {
            "statusCode": 201,
            "body": json.dumps({
                "job_id": info["job_id"],
                "applicant_id": email,
                "job_application_status": info["job_application_status"],
                "resumes": info["resumes"],
                "cover_letters": info["cover_letters"]
            })
        }
    else:
        return {
            "statusCode": 426,
            "body": json.dumps({
                "message": "Insufficient privileges to post a job application"
            }),
        }
