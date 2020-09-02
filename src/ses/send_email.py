import boto3
from botocore.exceptions import ClientError
from icalendar import Calendar, Event
from datetime import datetime

import uuid
import pytz

import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders

LOCAL_TZ = pytz.timezone("US/Eastern")

class Identity:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
def build_cal_event(event_name, event_description, \
                  organizer, attendees,\
                  dtstart, dtend):
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
'''.format(event_name.lower(), uuid.uuid4(), event_name))
    
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
STATUS:UNCONFIRMED
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

def send_email(sender, recipients, subject, body, ics=None):
    aws_region = "us-east-1"
    client = boto3.client('ses',region_name=aws_region)
    charset = "UTF-8"
    
    msg = MIMEMultipart('alternative')
    
    msg["Subject"] = subject
    msg["From"] = sender.email
    msg["To"] = ', '.join(map(lambda x: x.email, recipients))
    msg["Content-class"] = "urn:content-classes:calendarmessage"

    part = MIMEText(body)
    msg.attach(part)
    
    if ics != None:
        ics_name = "{}.ics".format(subject.replace(" ", "_").upper())
        part = MIMEBase('text', 'calendar',method='REQUEST',name=ics_name)
        
        part.set_payload(ics)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename={}".format(ics_name))
        part.add_header("Content-class", "urn:content-classes:calendarmessage")
        msg.attach(part)
    
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
    sender = Identity("Saima Ali", "saiima.ali@mail.utoronto.ca")
    recipients = [sender]
    subject = "Hello world"
    body = "lorem ipsum dolor sit amet"

    dtstart = datetime(2020, 8, 26, 21, 30, 0)
    dtend = datetime(2020, 8, 26, 22, 30, 0)
    #(event_name, event_description, \
    #                  organizer, attendees,\
    #                  dtstart, dtend)
    ics = build_cal_event("cat_screams", "He is rlly homgry", sender, recipients, dtstart, dtend)

    with open("event.ics", 'w') as f:
        f.write(ics)
        
    send_email(sender, recipients, subject, body, ics)
