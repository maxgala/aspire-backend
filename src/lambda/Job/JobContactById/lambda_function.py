import sys
import json
import logging

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import get_users, admin_update_credits
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
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return http_status.unauthorized()

    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)

    if job == None:
        session.close()
        return http_status.not_found()

    user_credits = int(get_users(filter_=("email", user['email']), \
        attributes_filter=["custom:credits"])[0]['attributes'].get('custom:credits'))
    email = user['email']
    if job.can_contact:
        applied = False
        for job_app in job.job_applications:
            if job_app.applicant_id == email:
                applied = True
        if not applied:
            session.close()
            return http_status.forbidden("You need to apply to the job before requesting contact-information")

        if job.people_contacted >= 4:
            session.close()
            return http_status.forbidden("Limit of contact information requests has been exceeded")

        if user_credits < 5:
            session.close()
            return http_status.forbidden("You do not have enough credits to request contact information")

        admin_update_credits(email, -5) # deducting credits for requesting contact_info
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
        session.close()
        return http_status.success(json.dumps({
                    "message": "Hiring manager does not want to be contacted"
                }))
