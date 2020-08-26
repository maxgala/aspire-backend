import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
import boto3

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    
    """
    #Commented out this authentication because we are planning to do some other way in the future
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
    
    user_att=getuserresponse['UserAttributes']
    mem_type = ''
    for att in user_att:
        if att['Name'] == 'custom:user_type':
            user_type = att['Value']
        elif att['Name'] == 'email':
            email = att['Value']
        elif att['Name'] == 'family_name':
            family_name = att['Value']
        elif att['Name'] == 'given_name':
            given_name = att['Value']
        try:
            if att['Name'] == 'custom:membership_type':
                mem_type = att['Value']
        except:
            pass
    
    if user_type == 'Mentor' or (user_type == 'Mentee' and mem_type == 'premium'):
    """
    info = json.loads(event["body"])
    
    tags = []
    for tag in info["job_tags"]:
        tags.append(JobTags[tag])
    # # create job
    Job_row = Job(title=info["title"], company=info["company"],
                    region=info["region"], city=info["city"], country=info["country"], job_type=JobType[info["job_type"]],
                    description=info["description"], requirements=info["requirements"], posted_by=info["posted_by"],
                    poster_family_name = info["poster_family_name"], poster_given_name = info["poster_given_name"],
                    job_status=JobStatus[info["job_status"]] if "job_status" in info else "OPEN",job_tags=tags, salary=info["salary"], deadline = info["deadline"])

    # # persists data
    session.add(Job_row)
    

    # # commit and close session
    
    session.commit()
    

    return {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Created Job Row",
            "job": row2dict(Job_row)
        }),
    }
    session.close()
    """
    else:
        return {
            "statusCode": 426,
            "body": json.dumps({
                "message": "You are not allowed to post a Job. Upgrade your membership"
            }),
        }
    """