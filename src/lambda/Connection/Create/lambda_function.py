import json
import logging

from connection import Connection, ConnectionStatus
from base import Session
from send_email import send_email, send_templated_email
from role_validation import UserType, check_auth
import http_status

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
        return http_status.unauthorized()

    body = json.loads(event["body"])
    try:
        requestor = body['requestor']
        requestee = body['requestee'] 
    except:
        return http_status.bad_request("missing body attribute(s): 'requestor' or 'requestee'")

    try:
        requestor_email = requestor['email']
        requestor_type = requestor['user_type']
        requestor_name = requestor['name']
        requestee_email = requestee['email']
        requestee_type = requestee['user_type']
        requestee_name = requestee['name']
    except:
        return http_status.bad_request("missing body attribute(s): 'user_type', 'email' or 'name'")

    session = Session()
    connections = session.query(Connection).all()
    create_conn = True
    for connection in connections:
        if (connection.requestor == requestor_email and connection.requestee == requestee_email) \
            or (connection.requestor == requestee_email and connection.requestee == requestor_email):
            if connection.connection_status == ConnectionStatus.PENDING:
                if connection.requestor == requestee_email and connection.requestee == requestor_email:
                    connection.connection_status = ConnectionStatus.ACCEPTED
                    email_subject = "[MAX Aspire] Your connection request was accepted!"
                    email_body = f"Salaam {requestor_name}!\r\n\nWe are delighted to confirm that you are now connected to {requestee_name}!\r\n\nYou will be able to chat and send direct messages to your connection. Engaging in direct communication we request our valued members to maintain high professional standards at all times.\r\n\nMAX Aspire is helping build strong communities. We value your commitment. Thank you for inspiring our aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
                    # send_email(to_addresses=[requestor_email, requestee_email], subject=email_subject, body_text=email_body)

                    template_data = {
                        "requestee_name": str(requestee_name),
                        "requestor_name": str(requestor_name)
                    }
                    template_data = json.dumps(template_data)
                    # recipients = [requestor_email,requestee_email]
                    recipients = ["tayyaabtanveer@gmail.com", "tayyaabtanveer+1@gmail.com"]
                    send_templated_email(recipients, "CreateConnection-RequestAccepted", template_data)    

                    create_conn = False
                    break

                session.close()
                return http_status.bad_request("connections request already sent")
            elif connection.connection_status == ConnectionStatus.ACCEPTED:
                session.close()
                return http_status.bad_request("connections request already established")

    if create_conn:
        if requestee_type == "MENTOR" and requestor_type == "MENTOR":
            new_connection = Connection(requestor=requestor_email, requestee=requestee_email, connection_status=ConnectionStatus.PENDING)
            session.add(new_connection)
            email_subject = "[MAX Aspire] Someone wants to connect with you!"
            email_body = f"Salaam {requestee_name}!\r\n\nYou are quite popular in the MAX Aspire community! {requestor_name} wants to connect with you. To accept or reject this request, please visit aspire.maxgala.com\r\n\nEngaging in direct communication members are requested to respect and maintain high professional standards at all times.\r\n\nMAX Aspire is helping build strong communities. We value your commitment. Thank you for inspiring our aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"
            # send_email(to_addresses=[requestee_email], subject=email_subject, body_text=email_body)
            template_data = {
                "requestee_name": str(requestee_name),
                "requestor_name": str(requestor_name)
            }
            template_data = json.dumps(template_data)
            # recipients = [requestee_email]
            recipients = ["tayyaabtanveer@gmail.com"]
            send_templated_email(recipients, "CreateConnection-RequesteeIsMentor", template_data)    



        elif requestee_type == "MENTEE" and requestor_type == "MENTOR":
            new_connection = Connection(requestor=requestor_email, requestee=requestee_email, connection_status=ConnectionStatus.ACCEPTED)
            session.add(new_connection)
            email_subject = "[MAX Aspire] Someone likes your resume!"
            email_body = f"Salaam {requestee_name}!\r\n\n{requestor_name} liked your resume and wants to connect with you!\r\n\nEngaging in direct communication members are requested to respect and maintain high professional standards at all times.\r\n\nMAX Aspire is helping build strong communities. We value your commitment. Thank you for inspiring our aspiring professionals.\r\n\nBest regards,\nTeam MAX Aspire\r\n"

            # The send_email_templated function requires JSON Formatted Data with " strings "
            template_data = {
                "requestee_name": str(requestee_name),
                "requestor_name": str(requestor_name)
            }
            template_data = json.dumps(template_data)
            # recipients = [requestor_email, requestee_email]
            recipients = ["tayyaabtanveer@gmail.com", "tayyaabtanveer+2@gmail.com"]
            send_templated_email(recipients, "CreateConnection-RequesteeIsMentee", template_data)           
            # send_email(to_addresses=[requestor_email, requestee_email], subject=email_subject, body_text=email_body)

        else:
            return http_status.bad_request("A connection can only be initiated by a mentor")

    session.commit()
    session.close()

    return http_status.success()
