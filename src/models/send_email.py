import os
import boto3
from botocore.exceptions import ClientError
# import icalendar
# from icalendar import Calendar, Event
from datetime import datetime

import uuid
import pytz

import email
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
COMMASPACE = ', '

LOCAL_TZ = pytz.timezone("US/Eastern")

BODY_HTML = """\
<html>
<head></head>
<body>
<h1></h1>
<p>How are you?</p>
</body>
</html>
"""
CRLF = "\r\n"

class Identity:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
def build_cal_event(event_name, event_description, \
                  organizer, attendees,\
                  dtstart, dtend):
    # cal = icalendar.Calendar()
    str_list = []
    str_list.append('''\
BEGIN:VCALENDAR
METHOD:REQUEST
PRODID:MAX Aspire Calendar Event
VERSION:2.0
BEGIN:VTIMEZONE
TZID:Eastern Standard Time
BEGIN:STANDARD
DTSTART:16010101T020000
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
RRULE:FREQ=YEARLY;INTERVAL=1;BYDAY=1SU;BYMONTH=11
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:16010101T020000
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
RRULE:FREQ=YEARLY;INTERVAL=1;BYDAY=2SU;BYMONTH=3
END:DAYLIGHT
END:VTIMEZONE
BEGIN:VEVENT
''')
    str_list.append("ORGANIZER;CN={0}:mailto:{1}\n".format(organizer.name, \
                                                         organizer.email))
    attendee_str = ""
    for attendee in attendees:
        str_part = '''\
ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={0}:
 mailto:{1}
'''.format(attendee.name, attendee.email)
        attendee_str += str_part

    str_list.append(attendee_str)
    str_list.append('''\
DESCRIPTION;LANGUAGE=en-US:{0}
UID:{1}
SUMMARY;LANGUAGE=en-US:{2}
'''.format(event_description.lower(), uuid.uuid4(), event_name))
    
    dtstart_as_string = dtstart.strftime("%Y%m%dT%H%M%S")
    dtend_as_string = dtend.strftime("%Y%m%dT%H%M%S")

    str_list.append('''\
DTSTART;TZID=Eastern Standard Time:{0}
DTEND;TZID=Eastern Standard Time:{1}
'''.format(dtstart_as_string, dtend_as_string))

    str_list.append('''\
CLASS:PUBLIC
PRIORITY:5
DTSTAMP:{0}
TRANSP:OPAQUE
STATUS:CONFIRMED
SEQUENCE:0
LOCATION;LANGUAGE=en-US:
X-MICROSOFT-CDO-APPT-SEQUENCE:0
X-MICROSOFT-CDO-OWNERAPPTID:2118692743
X-MICROSOFT-CDO-BUSYSTATUS:TENTATIVE
X-MICROSOFT-CDO-INTENDEDSTATUS:BUSY
X-MICROSOFT-CDO-ALLDAYEVENT:FALSE
X-MICROSOFT-CDO-IMPORTANCE:1
X-MICROSOFT-CDO-INSTTYPE:0
X-MICROSOFT-ONLINEMEETINGEXTERNALLINK:
X-MICROSOFT-ONLINEMEETINGCONFLINK:
X-MICROSOFT-DONOTFORWARDMEETING:FALSE
X-MICROSOFT-DISALLOW-COUNTER:FALSE
X-MICROSOFT-LOCATIONS:[]
BEGIN:VALARM
DESCRIPTION:REMINDER
TRIGGER;RELATED=START:-PT15M
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
'''.format(datetime.now().strftime("%Y%m%dT%H%M%SZ")))

    
    cal = ''.join(str_list)
    return cal

def send_email(sender, recipients, subject, body_text, body_html, ics=None):
    aws_region = "us-east-1"
    client = boto3.client('ses',region_name=aws_region)

    if ics != None:
        ics_name = "{}.ics".format(subject.replace(" ", "_").upper())
    
    msg = MIMEMultipart('mixed')

    msg["Subject"] = subject
    msg["From"] = sender.email
    msg["To"] = ', '.join(map(lambda x: x.email, recipients))

    msgAlternative = MIMEMultipart('alternative')

    bodycontent= CRLF+body_text
    textpart = MIMEText(bodycontent, 'plain')
    htmlpart = MIMEText(body_html, 'html')
    calpart = MIMEText(ics,'calendar;method=REQUEST')

    msgAlternative.attach(textpart)
    msgAlternative.attach(htmlpart)
    msgAlternative.attach(calpart)

    if ics != None:
        ics_name = "{}.ics".format(subject.replace(" ", "_").upper())
        ical_atch = MIMEBase('text', 'calendar', **{'method' : 'REQUEST', 'name' : ics_name})
        ical_atch.set_payload(ics)
        encoders.encode_base64(ical_atch)
        ical_atch.add_header('Content-Disposition', "attachment; filename={}".format(ics_name))
        ical_atch.add_header('Content-class', 'urn:content-classes:calendarmessage')
    
    msg.attach(msgAlternative)
    msg.attach(ical_atch)
         
    try:
        result = client.send_raw_email(
            Source=msg['From'],
            Destinations=[recipient.email for recipient in recipients],
            RawMessage={'Data': msg.as_string()}
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(result['MessageId'])

def send_email_Outlook(sender, recipients, subject, body, ics=None):
    aws_region = "us-east-1"
    client = boto3.client('ses',region_name=aws_region)
    charset = "UTF-8"

    msg = MIMEMultipart('alternative')
    
    # msg["Subject"] = subject
    msg["From"] = sender.email
    msg["To"] = ', '.join(map(lambda x: x.email, recipients))
    msg["Content-class"] = "urn:content-classes:calendarmessage"

    part_email = MIMEText(BODY_HTML,"html")
    part_cal = MIMEText(ics,'calendar;method=REQUEST', charset)

    msg.attach(part_email)
    msg.attach(part_cal)
    
    try:
        result = client.send_raw_email(
            Source=msg['From'],
            Destinations=[recipient.email for recipient in recipients],
            RawMessage={'Data': msg.as_string()}
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(result['MessageId'])

def send_email_Jobs(sender, recipients, subject, body, JobName, JobDate):
    aws_region = "us-east-1"
    client = boto3.client('ses',region_name=aws_region)
    charset = "UTF-8"
    named_tuple = time.localtime() # get struct_time
    today = time.strftime("%Y-%m-%d", named_tuple)

    msg = MIMEMultipart('mixed')
    
    msg["Subject"] = subject
    msg["From"] = sender.email
    msg["To"] = ', '.join(map(lambda x: x.email, recipients))

    bodytext = f"Salaam!\r\n\nWe would like to notify that [Candidate Name] has applied to the job posting {JobName} on {today}. The aforementioned job was posted on MAX Aspire job board on {JobDate}. Kindly login to your account to access the complete profile and application of the candidate. Once the application is reviewed the status can be changed to “Under Review”, “Invite for interview” or “Rejected”.\r\n\n Please note that the candidate is more responsive in the first 2 weeks of applying the job. If the job posting is unavailable for any reason kindly contact the support team ASAP.\r\n\nBest regards,\n[TEAM MAX ASPIRE]\r\n"
    
    bodyhtml = """\
    <html>
    <head></head>
    <body>
    <p>Salaam!</p>
    <p>We would like to notify that [Candidate Name] has applied to the job posting [POSTING DETAILS] on [Date Applied]
. The aforementioned job was posted on MAX Aspire job board on [DATE]. Kindly login to your
        account to access the complete profile and application of the candidate. Once the application is reviewed the the status can be changed to “Under Review”, “Invite for interview” or “Rejected”.
    <p>Please note that the candidate is more responsive in the first 2 weeks of applying the job. If the job posting is
unavailable for any reason kindly contact the support team ASAP.</p>
<p>Best regards,<br>
[TEAM MAX ASPIRE] </p>
    </body>
    </html>
    """

    msgBody = MIMEMultipart('alternative')

    textpart = MIMEText(bodytext.encode(charset), 'plain', charset)

    msgBody.attach(textpart)

    msg.attach(msgBody)
    
    try:
        result = client.send_raw_email(
            Source=msg['From'],
            Destinations=[recipient.email for recipient in recipients],
            RawMessage={'Data': msg.as_string()}
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(result['MessageId'])

if __name__ == "__main__":
    outlookrec= []
    AllOtherrec= []
    sender = Identity("Abdullah Siddiqui", "siddiquiabdullah92@gmail.com")
    rec1= Identity("Abdullah", "siddiquiabdullah92@outlook.com")
    recipients = [rec1]
    numRecepients= len(recipients)
    
    i= 0
    while i < numRecepients:
        if "outlook" in recipients[i].email:
            outlookrec.append(recipients[i])
        else:
            AllOtherrec.append(recipients[i])
        i += 1
    
    subject = "Hello world"
    body = "lorem ipsum dolor sit amet"

    dtstart = datetime(2020, 9, 9, 22, 15, 0)
    dtend = datetime(2020, 9, 9, 22, 30, 0)

    ics = build_cal_event("cat_screams", "He is rlly homgry", sender, recipients, dtstart, dtend)

    with open("event.ics", 'w') as f:
        f.write(ics)
    
    if len(AllOtherrec) > 0:      
        send_email(sender, AllOtherrec, subject, body, ics)
    if len(outlookrec) > 0:
        send_email_Outlook(sender, outlookrec, subject, body, ics)



