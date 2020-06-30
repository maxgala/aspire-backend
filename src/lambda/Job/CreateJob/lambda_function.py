import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from user import User, UserType, MembershipType, IndustryTags, EducationLevel
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
        
        tags = []
        for tag in info["job_tags"]:
            tags.append(JobTags[tag])
        # # create job
        Job_row = Job(title=info["title"], company=info["company"],
                        region=info["region"], city=info["city"], country=info["country"], job_type=JobType[info["job_type"]],
                        description=info["description"], requirements=info["requirements"],
                        posted_by=info["posted_by"], contact_email=info["contact_email"], job_status=JobStatus[info["job_status"]],
                        job_tags=tags, salary=info["salary"], deadline = datetime.strptime(info["deadline"], '%m-%d-%Y').date())
    
        # # persists data
        session.add(Job_row)
        

        # # commit and close session
        
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Created Job Row"
            }),
        }
    else:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "message": "You are not allowed to post a Job"
            }),
        }
