import json
import logging

from connect_se import ConnectSE, ConnectStatus
from base import Session
from send_email import send_email
# from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_groups = [
    #     UserGroups.ADMIN,
    #     UserGroups.MENTOR,
    #     UserGroups.FREE,
    #     UserGroups.PAID
    # ]
    # err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    # if err:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": group_response
    #         })
    #     }

    body = json.loads(event["body"])
    try:
        requestor = body['requestor']
        requestee = body['requestee'] 
    except:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'requestor' or 'requestee'"
            })
        }

    try:
        requestor_email = requestor['email']
        requestor_type = requestor['user_type']
        requestee_email = requestee['email']
        requestee_type = requestee['user_type']
    except:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'user_type' or 'email'"
            })
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
                    # TODO: dynamic user_email
                    # TODO: update email subject/body
                    user_email = "saleh.bakhit@hotmail.com"
                    email_subject = "Your Senior Executive connection request was accepted"
                    email_body = "<name> has accepted your connection request!"
                    send_email(to_addresses=user_email, subject=email_subject, body_text=email_body)

                    create_conn = False
                    break

                session.close()
                return {
                    "statusCode": 409,
                    "body": json.dumps({
                        "errorMessage": "connections request already sent"
                    })
                }
            elif connection.connect_status == ConnectStatus.ACCEPTED:
                session.close()
                return {
                    "statusCode": 409,
                    "body": json.dumps({
                        "errorMessage": "connections request already established"
                    })
                }

    if create_conn:
        if requestee_type == "MENTOR" and requestor_type == "MENTOR":
            ConnectSE_new = ConnectSE(requestor=requestor_email, requestee=requestee_email, connect_status=ConnectStatus.PENDING)
            session.add(ConnectSE_new)
            email_subject = "You have received a new Senior Executive connection request"
            email_body = "<name> has requested to connect with you"
            user_email = "saleh.bakhit@hotmail.com"
            send_email(to_addresses=[user_email], subject=email_subject, body_text=email_body)

        elif requestee_type == "MENTEE" and requestor_type == "MENTOR":
            ConnectSE_new = ConnectSE(requestor=requestor_email, requestee=requestee_email, connect_status=ConnectStatus.ACCEPTED)
            session.add(ConnectSE_new)
            email_subject = "A senior executive has connected with you!"
            email_body = "<name> viewed your profile from the resume bank and has connected with you!"
            send_email(to_addresses=[requestor_email, requestee_email], subject=email_subject, body_text=email_body)

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "errorMessage": "A connection can only be initiated by a mentor"
                })
            }


        # TODO: dynamic user_email
        # TODO: update email subject/body
        # TODO: retrieve requestor email from authorization

    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
