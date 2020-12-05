import logging
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from ics.icalendar import Calendar, Event
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses_client = boto3.client('ses')

ADMIN_EMAIL = "aspire@maxgala.com"

def build_calendar_invite(name, description, start, end, to_addresses, source_email=ADMIN_EMAIL):
    ics = Calendar()
    ics.events.add(Event(name, start, end, description=description, attendees=to_addresses, organizer=source_email))

    return str(ics)

def send_email(to_addresses, subject, body_text, source_email=ADMIN_EMAIL, charset="UTF-8", ics=None):   
    msg = MIMEMultipart('mixed')

    msg_text = MIMEText(body_text, 'plain', charset)
    msg.attach(msg_text)

    msg['Subject'] = Header(subject, charset) 

    if ics != None:
        msg_cal = MIMEBase('text', 'calendar', **{'method' : 'REQUEST', 'name' : 'MAX Aspire Calendar Event'})
        msg_cal.set_payload(ics)
        msg_cal.add_header('Content-Type', 'text/calendar;method=REQUEST', name='invite.ics')
        msg.attach(msg_cal)

    if not isinstance(to_addresses, list):
        to_addresses = [to_addresses]
    try:
        response = ses_client.send_raw_email(
            Source=source_email,
            Destinations=to_addresses,
            RawMessage={
                'Data': msg.as_string(),
            },
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        raise e
    else:
        logger.info("Email sent! Message ID:"),
        logger.info(response['MessageId'])