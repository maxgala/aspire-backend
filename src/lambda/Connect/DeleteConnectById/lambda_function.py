import json
from connect_se import *
from base import Session

def handler(event, context):
    connect_id = event["pathParameters"]["connectId"]

    session = Session()
    connect = session.query(ConnectSE).get(connect_id)

    if connect != None:
        session.delete(connect)
        session.commit()
        session.close()
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Connect Row with ID {} deleted".format(connect_id)
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
