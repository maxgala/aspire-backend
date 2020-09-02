import json
from connect_se import *
from base import Session


def handler(event, context):
    # info = json.loads(event["body"])
    connect_id = event["pathParameters"]["connectId"]
    
    session = Session()
    connect = session.query(ConnectSE).get(connect_id)

    if connect != None:
        attrs_to_update = info.keys()
        for attr in attrs_to_update:
            if attr == "connect_status":
                setattr(connect, attr, ConnectStatus(int(info[attr])))
            else:
                setattr(connect, attr, info[attr])
            
        session.commit()
        session.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
            "message": "Updated Connect Row, with ID {}".format(connect_id)
            })
        }
    
    else:
        session.close()
        
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in Connect table".format(connect_id)
            })
        }
