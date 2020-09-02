import json
from connect_se import *
from base import Session


def handler(event, context):
    # info = json.loads(event["body"])
    connect_id = event["pathParameters"]["connectId"]
    
    session = Session()
    connect = session.query(ConnectSE).get(connect_id)
    name = "Saima"
    acceptor = "saiima.ali@mail.utoronto.ca"
    requestor = "saiima.ali@mail.utoronto.ca"

    email_subject = "Your Senior Executive connection request was accepted."
    email_body = "{} has accepted your connection request! You can connect them at {}".format(name, acceptor)
    

    if connect != None:

        try:
            
            result = client.send_raw_email(
                Source=msg['From'],
                Destinations=[recipient.email for recipient in recipients],
                RawMessage={'Data': msg.as_string()}

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
    else:
        session.close()
        
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in Connect table".format(connect_id)
            })
        }
