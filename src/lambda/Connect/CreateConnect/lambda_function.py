import json
from connect_se import *

from base import Session


def handler(event, context):
    info = json.loads(event["body"])
    session = Session()

    connect_se = ConnectSE()
    attribs = dir(ConnectSE)
    manual_attribs = ['connect_status']

    for attrib in attribs:
        if attrib in manual_attribs:
            if attrib == "connect_status":
                #default to pending
                setattr(connect_se, attrib, ConnectStatus.PENDING)
        elif not (attrib.startswith('_') or attrib.strip() == "metadata"):
            try:
                setattr(connect_se, attrib, info[attrib])
            except: # in case underspecified?
                continue
            
    name = "Saima"
    recipient = "saiima.ali@mail.utoronto.ca"
    requestor = "saiima.ali@mail.utoronto.ca"

    email_subject = "You have received a new Senior Executive connection request"
    email_body = "{} has requested to connect with you. Click here to accept.".format(name)
    # need to link to api ... force log in session
                
    try:
        result = client.send_raw_email(
            Source=requestor, # need SES verified email, using mine for now...
            Destinations=recipient,
            RawMessage={'Data': email_body}

        )
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
            "message": "Cannot send email to {}".format(requestor)
        })
    }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
            "message": "Accepted Connect, with ID {}".format(connect_id)
        })
    }
    
    session.add(connect_se)
    session.commit()
    session.refresh(connect_se)
    session.close()
    
    attribs = []
    pruned_attribs = ["connect_id"]

    for attrib in dir(ConnectSE):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            attribs.append(attrib)
            
    json_dict = {}
    for attrib in attribs:
        json_dict[attrib] = str(getattr(connect_se, attrib)) 

    return {
        "statusCode": 200,
        "body": json.dumps(json_dict)
    }
