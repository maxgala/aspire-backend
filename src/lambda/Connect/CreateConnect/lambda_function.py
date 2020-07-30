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
