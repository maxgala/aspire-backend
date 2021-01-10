import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserType, check_auth
from send_email import send_templated_email
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    session = Session()

    info = json.loads(event["body"])

    tags = []

    tag = info.get('job_tags')
    job_title = info.get('title')
    company = info.get('company')
    region = info.get('region')
    city = info.get('city')
    country = info.get('country')
    job_type = info.get('job_type')
    description = info.get('description')
    requirements = info.get('requirements')
    posted_by = info.get('posted_by')
    poster_family_name = info.get('poster_family_name')
    poster_given_name = info.get('poster_given_name')
    job_status = "UNDER_REVIEW"
    salary = info['salary']
    deadline = info.get('deadline')
    can_contact = str(info.get('can_contact'))

    #Validate body
    if not (tag and job_title and company and region and city and country and job_type and description and requirements and posted_by
            and poster_family_name and poster_given_name and job_status and salary and deadline and can_contact):
        return http_status.bad_request("missing parameter(s)")
    else:
        # If no attributes are missing, cast types as required.
        try:
            salary = int(salary)
            deadline = datetime.fromtimestamp(deadline).replace(hour=0, minute=0,second=0, microsecond=0)
            
            if can_contact.lower() == 'true':
                can_contact = True
            elif can_contact.lower() == 'false':
                can_contact = False 
            else:
                raise ValueError

            job_type = JobType[job_type]
            for tag in info["job_tags"]:
                tags.append(JobTags[tag])
        except:
            return http_status.bad_request("invalid parameter(s): 'salary must be an integer, deadline must be a datetime, can_contact must be a bool, and JobType & JobTags must be from their enum types'")


    Job_row = Job(title = job_title, company = company, region = region,
                    city = city, country = country, job_type = job_type,
                    description = description, requirements = requirements, posted_by = posted_by,
                    poster_family_name = poster_family_name, poster_given_name = poster_given_name,
                    job_status = job_status, job_tags = tags, salary = salary, deadline = deadline, can_contact = can_contact)

    session.add(Job_row)        
    session.commit()
    res = row2dict(Job_row)
    session.close()

    ##email hiring manager
    job_title = info["title"]
    today = datetime.today().strftime("%Y-%m-%d")
    hiring_manager = str(info["posted_by"])  

    # The send_email_templated function requires JSON Formatted Data with " strings "
    template_data = {
        "job_title": str(job_title),
        "today": str(today)
    }
    template_data = json.dumps(template_data)
    recipients = [hiring_manager]
    send_templated_email(recipients, "CreateJob", template_data)

    return http_status.success(json.dumps(res))