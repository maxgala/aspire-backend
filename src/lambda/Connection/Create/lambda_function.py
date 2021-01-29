import json
import logging

from connection import Connection, ConnectionStatus
from base import Session
from send_email import send_templated_email
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

                    template_data = {
                        "requestee_name": str(requestee_name),
                        "requestor_name": str(requestor_name)
                    }
                    template_data = json.dumps(template_data)
                    recipients = [requestor_email,requestee_email]
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

            template_data = {
                "requestee_name": str(requestee_name),
                "requestor_name": str(requestor_name)
            }
            template_data = json.dumps(template_data)
            recipients = [requestee_email]
            send_templated_email(recipients, "CreateConnection-RequesteeIsMentor", template_data)    



        elif requestee_type == "MENTEE" and requestor_type == "MENTOR":
            new_connection = Connection(requestor=requestor_email, requestee=requestee_email, connection_status=ConnectionStatus.ACCEPTED)
            session.add(new_connection)

            # The send_templated_email function requires JSON Formatted Data with " strings "
            template_data = {
                "requestee_name": str(requestee_name),
                "requestor_name": str(requestor_name)
            }
            template_data = json.dumps(template_data)
            recipients = [requestor_email, requestee_email]
            send_templated_email(recipients, "CreateConnection-RequesteeIsMentee", template_data)           

        else:
            return http_status.bad_request("A connection can only be initiated by a mentor")

    session.commit()
    session.close()

    return http_status.success()
