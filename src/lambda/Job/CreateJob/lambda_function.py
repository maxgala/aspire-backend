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

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    # FOR REFERENCE
    # # create a new session
    session = Session()
    info = json.loads(event["body"])
    
    tags = []
    for tag in info["job_tags"]:
        print(tag)
        tags.append(JobTags[tag])
    print(tags)
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
