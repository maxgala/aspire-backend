import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    #### The following code until the end of return should be commented out in order to run the functions locally
    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID
    ]
    err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    if err:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": group_response
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
    
    return {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Created Job Row",
            "job": job_dict
        }),
    }
    