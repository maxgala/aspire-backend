import json
import logging

from connect_se import ConnectSE, ConnectStatus
from base import Session
from send_email import send_email
from role_validation import UserType, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.FREE,
        UserType.PAID
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    body = json.loads(event["body"])
    try:
        requestor = body['requestor']
        requestee = body['requestee'] 
    except:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'requestor' or 'requestee'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    try:
        requestor_email = requestor['email']
        requestor_type = requestor['user_type']
        requestor_name = requestor['name']
        requestee_email = requestee['email']
        requestee_type = requestee['user_type']
        requestee_name = requestee['name']
    except:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'user_type', 'email' or 'name'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }        

    # if ACCEPTED exists (in either direction) => Conflict (409)
    # if PENDING exists (in the direction of the request) => Conflict (409)
    # if PENDING exists (in the direction opposite to the request) => change status to ACCEPTED
    # else => create new record with PENDING status
    session = Session()
    connect_ses = session.query(ConnectSE).all()
    create_conn = True
    for connection in connect_ses:
        if (connection.requestor == requestor_email and connection.requestee == requestee_email) \
            or (connection.requestor == requestee_email and connection.requestee == requestor_email):
            if connection.connect_status == ConnectStatus.PENDING:
                if connection.requestor == requestee_email and connection.requestee == requestor_email:
                    connection.connect_status = ConnectStatus.ACCEPTED
                    email_subject = "[MAX Aspire] Your connection request was accepted!"
                    email_body = f"Salaam!\r\n\nWe are delighted to confirm that you are now connected to {requestee_name}!\r\n\nYou will be able to chat and send direct messages to your connection. Engaging in direct communication we request our valued members to maintain high professional standards at all times.\r\n\nMAX Aspire is helping build strong communities. We value your commitment. Thank you for inspiring our aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
                    send_email(to_addresses=requestor_email, subject=email_subject, body_text=email_body)

                    create_conn = False
                    break

                session.close()
                return {
                    "statusCode": 409,
                    "body": json.dumps({
                        "errorMessage": "connections request already sent"
                    }),
                    "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
                }
            elif connection.connect_status == ConnectStatus.ACCEPTED:
                session.close()
                return {
                    "statusCode": 409,
                    "body": json.dumps({
                        "errorMessage": "connections request already established"
                    }),
                    "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
                }

    if create_conn:
        if requestee_type == "MENTOR" and requestor_type == "MENTOR":
            ConnectSE_new = ConnectSE(requestor=requestor_email, requestee=requestee_email, connect_status=ConnectStatus.PENDING)
            session.add(ConnectSE_new)
            email_subject = "[MAX Aspire] Someone wants to connect with you!"
            email_body = f"Salaam!\r\n\nYou are quite popular in the MAX Aspire community! {requestor_name} wants to connect with you. To accept or reject this request, please visit aspire.maxgala.com\r\n\nEngaging in direct communication members are requested to respect and maintain high professional standards at all times.\r\n\nMAX Aspire is helping build strong communities. We value your commitment. Thank you for inspiring our aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
            send_email(to_addresses=[requestor_email], subject=email_subject, body_text=email_body)

        elif requestee_type == "MENTEE" and requestor_type == "MENTOR":
            ConnectSE_new = ConnectSE(requestor=requestor_email, requestee=requestee_email, connect_status=ConnectStatus.ACCEPTED)
            session.add(ConnectSE_new)
            email_subject = "[MAX Aspire] Someone likes your resume!"
            email_body = f"Salaam {requestee_name}!\r\n\n{requestor_name} liked your resume and wants to connect with you!\r\n\nEngaging in direct communication members are requested to respect and maintain high professional standards at all times.\r\n\nMAX Aspire is helping build strong communities. We value your commitment. Thank you for inspiring our aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
            send_email(to_addresses=[requestor_email, requestee_email], subject=email_subject, body_text=email_body)

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "errorMessage": "A connection can only be initiated by a mentor"
                }),
                "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    session.commit()
    session.close()

    return {
        "statusCode": 201,
        "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
    }
