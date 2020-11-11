import logging
from datetime import datetime

from job import Job
from base import Session
from send_email import send_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info('## BEGIN')
    logger.info('Starting to approve jobs posted > 24 hours ago')

    session = Session()
    jobs = session.query(Job).filter(Job.job_status == 'UNDER_REVIEW')
    num_seconds_24_hours = 24*60*60
    for job in jobs:
        if datetime.now().timestamp() - job.created_on >= num_seconds_24_hours:
            job.job_status = 'ACTIVE'
            job_title = job.title
            today = datetime.today().strftime("%Y-%m-%d")
            hiring_manager = job.posted_by    
            subject = "[MAX Aspire] Your job is now active!"
            body = f"Salaam!\r\n\nWe are delighted to confirm that the job posting {job_title} is successfully posted on MAX Aspire job board on {today}. You will frequently be notified about the job applications as and when received. Keep an eye on your member portal/email.\r\n\nWe appreciate you putting your trust in MAX Aspire. We wish you luck in hiring the best possible candidate form our talented pool of aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
            send_email(to_addresses=hiring_manager, subject=subject, body_text=body)
    session.commit()
    session.close()

    logger.info('## END')