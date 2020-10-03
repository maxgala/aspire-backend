import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses_client = boto3.client('ses')

ADMIN_EMAIL = "saiima.ali@mail.utoronto.ca"

def send_email(to_addresses, subject, body_text, source_email=ADMIN_EMAIL, charset="UTF-8"):
    if not isinstance(to_addresses, list):
        to_addresses = [to_addresses]
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': to_addresses,
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=source_email,
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
    else:
        logger.info("Email sent! Message ID:"),
        logger.info(response['MessageId'])
