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
import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    id_token = (event['headers']['Authorization']).split('Bearer ')[1]
    user = jwt.decode(id_token, verify=False)

    session = Session()

    user_type = user['custom:user_type']
    mem_type = user['custom:membership_type']
    
    if user_type == 'Mentor' or (user_type == 'Mentee' and mem_type == 'premium'):
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
        session.close()
        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Created Job Row",
                "job": row2dict(Job_row)
            }),
        }
    else:
        return {
            "statusCode": 426,
            "body": json.dumps({
                "message": "You are not allowed to post a Job. Upgrade your membership"
            }),
        }