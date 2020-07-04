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

    getuserresponse =client.get_user(
            AccessToken=access_token
        )
    User_Att=getuserresponse['UserAttributes']
    Mem_type = ''
    for att in User_Att:
        if att['Name'] == 'custom:user_type':
            User_type = att['Value']
        try:
            if att['Name'] == 'custom:membership_type':
                Mem_type = att['Value']
        except:
            pass
    print(User_type)
    print(Mem_type)
    if User_type == 'Mentor' or (User_type == 'Mentee' and Mem_type == 'premium'):

        info = json.loads(event["body"])

        Job_application_row = JobApplication(
            job_id = info["job_id"],
            applicant_id = info["applicant_id"],
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
            "statusCode": 200,
            "body": json.dumps(info),
        }
    else:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "message": "Insufficient privileges to post a job application"
            }),
        }