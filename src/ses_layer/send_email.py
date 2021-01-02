import logging
import boto3
import pytz
import uuid
import django
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from email.encoders import encode_base64
from icalendar import Calendar, Event, Timezone, TimezoneDaylight, TimezoneStandard
from datetime import datetime
from django.template import Template, Context
from django.conf import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses_client = boto3.client('ses')

ADMIN_EMAIL = "aspire@maxgala.com"

BODY_TEMPLATE = """\
<html>
<body>
<p>{{body}}</p>
</body>
</html>
"""

settings.configure(TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
    },
])
django.setup()

def build_calendar_invite(name, description, start, end, to_addresses, source_email=ADMIN_EMAIL,charset="UTF-8"):
    # prepare calendar with timezone
    ics = Calendar()
    ics.add('prodid', '-//MAX Aspire//-')
    ics.add('version', '2.0')
    ics.add('method','REQUEST')
    tz = pytz.timezone("America/Toronto")
    timezone = create_timezone(tz)
    ics.add_component(timezone)

    # prepare event with all fields
    e = Event()
    for i in range(0,len(to_addresses)):
        e.add('attendee', to_addresses[i])
    e.add('organizer', source_email)    
    e.add('summary', name)
    e.add('created',tz.localize(datetime.now()))
    e.add('description', description)
    e.add('dtstart', tz.localize(start))
    e.add('dtend', tz.localize(end))
    e.add('dtstamp',tz.localize(datetime.now()))
    e.add('last-modified',tz.localize(datetime.now()))
    e.add('sequence',0)
    e.add('priority',5)
    e.add('uid',uuid.uuid4())
    ics.add_component(e)

    ics = ics.to_ical().decode(charset) 

    return ics


def send_email(to_addresses, subject, body_text, source_email=ADMIN_EMAIL, charset="UTF-8", ics=None):   
    if not isinstance(to_addresses, list):
        to_addresses = [to_addresses]

    msg = MIMEMultipart('alternative')

    msg["Subject"] = subject
    msg["From"] = source_email
    msg["To"] = ", ".join(to_addresses)
    msg["Content-class"] = "urn:content-classes:calendarmessage"

    # Attach message body
    t = Template(BODY_TEMPLATE)
    c = Context({'body':body_text})
    text = t.render(c).replace('\n','<br />')
    msg_text = MIMEText(text,"html")
    msg.attach(msg_text)

    # Attach calendar invite
    if ics != None:
        msg_cal = MIMEText(ics,'calendar;method=REQUEST', charset)
        msg.attach(msg_cal) 

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


def create_timezone(tz):
    # Function from https://github.com/pimutils/khal/blob/64d70e3eb59570cfd3af2e10dbbcf0a26bf89111/khal/khalendar/event.py#L287

    first_date = datetime.today() 
    last_date = datetime.today() 
    timezone = Timezone()
    timezone.add('TZID', tz)

    dst = {one[2]: 'DST' in two.__repr__() for one, two in tz._tzinfos.items()}

    first_num, last_num = 0, len(tz._utc_transition_times) - 1
    first_tt = tz._utc_transition_times[0]
    last_tt = tz._utc_transition_times[-1]
    for num, dt in enumerate(tz._utc_transition_times):
        if dt > first_tt and dt < first_date:
            first_num = num
            first_tt = dt
        if dt < last_tt and dt > last_date:
            last_num = num
            last_tt = dt

    for num in range(first_num, last_num + 1):
        name = tz._transition_info[num][2]
        if dst[name]:
            subcomp = TimezoneDaylight()
            rrule = {'freq': 'yearly', 'bymonth': 3, 'byday': '2su'}
        else:
            subcomp = TimezoneStandard()
            rrule = {'freq': 'yearly', 'bymonth': 11, 'byday': '1su'} 

        subcomp.add('TZNAME', tz._transition_info[num][2])
        subcomp.add('DTSTART',tz.fromutc(tz._utc_transition_times[num]).replace(tzinfo=None))
        subcomp.add('TZOFFSETTO', tz._transition_info[num][0])
        subcomp.add('TZOFFSETFROM', tz._transition_info[num - 1][0])
        subcomp.add('RRULE',rrule)
        timezone.add_component(subcomp)

    return timezone

event_name = 'MAX Aspire Coffee Chat'
subject = '[MAX Aspire] 1 on 1 coffee chat confirming the attendees'
email = 'test_mentee_paid_1@outlook.com'
mentee_body = f"Salaam!\nWe are delighted to confirm your 1 on 1 coffee chat with Naba.\nYour coffee chat will take place on: \n\nPlease connect with the Senior Executive to find a time that works for both of you.\nPlease make sure of your attendance. In case of any changes in the circumstances contact the support team at your earliest.\n\nBest regards,\n\nThe MAX Aspire Team"
ics = build_calendar_invite(event_name, subject, datetime(2021, 12, 31, 9, 00), datetime(2021, 12, 31, 10, 00), [email])
send_email(email, subject, mentee_body, ics=ics)
