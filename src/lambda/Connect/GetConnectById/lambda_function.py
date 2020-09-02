import json
from connect_se import *
from base import Session

def handler(event, context):
    connect_id = event["pathParameters"]["connectId"]

    session = Session()
    connect_se = session.query(ConnectSE).get(connect_id)
    session.close()

    attribs = []
    pruned_attribs = ["connect_id"]

    for attrib in dir(ConnectSE):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            attribs.append(attrib)
    
    if connect_se != None:
        # construct JSON-able dictionary
        json_dict = {}
        for attrib in attribs:
            json_dict[attrib] = str(getattr(connect_se, attrib)) 
            
        return {"statusCode": 200,
                "body": json.dumps(json_dict)
        }
        
    
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in ConnectSE table".format(connect_id)
            })
        }
