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
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    
    if job == None:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID not found"
            })
        }
    
    try:
        access_token = (event['headers']['Authorization']).replace('Bearer ', '')
    except:
        return {
        "statusCode": 401,
        "body": json.dumps({
            "message": "Authorization header is expected"
        }),
    }
    
    getuserresponse = client.get_user(
        AccessToken=access_token
    )
    user_att=getuserresponse['UserAttributes']
    credit = 0
    for att in user_att:
        try:
            if att['Name'] == 'custom:credits':
                credit = att['Value']
        except:
            pass
        if att['Name'] == 'email':
            email = att['Value']
    '''
    mem_type = ''
    credit = 0
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
        try:
            if att['Name'] == 'custom:credits':
                credit = att['Value']
        except:
            pass
    if user_type == 'Mentor' or (user_type == 'Mentee' and mem_type == 'premium'):
    '''
    
    applied = False
    for job_app in job.job_applications:
        if job_app.applicant_id == email:
            applied = True
    if not applied:
        return {
            "statusCode": 428,
            "body": json.dumps({
                "message": "You need to apply to the job before requesting contact-information"
            })
        }

    if job.people_contacted >= 4:
        return {
            "statusCode": 417,
            "body": json.dumps({
                "message": "Limit of contact information requests has been exceeded"
            })
        }
    print(credit)
    if int(credit) < 5:
        return {
            "statusCode": 402,
            "body": json.dumps({
                "message": "You do not have enough credits to request contact information"
            })
        }
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
    return {
        "statusCode": 200,
        "body": json.dumps({
            "contact_details": {
                    "email" : job.posted_by,
                    "given_name" : job.poster_given_name,
                    "family_name" : job.poster_family_name
                }   
        })
    }
    '''
    else:
        return {
            "statusCode": 426,
            "body": json.dumps({
                "message": "You are not allowed to view the contact information of the job poster. Upgrade membership"
            }),
        }
    '''    
    # # commit and close session
    session.close()