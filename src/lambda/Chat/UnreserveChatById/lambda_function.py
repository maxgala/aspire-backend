import json
from chat import *

from base import Session
from sqlalchemy.types import DateTime
from datetime import datetime
import boto3
import jwt

client = boto3.client('cognito-idp')


def handler(event, context):

    access_token = event['headers']['X-Aspire-Access-Token']

    # ----------------- User validation ------------------
    id_token = (event['headers']['Authorization']).split('Bearer ')[1]
    user = jwt.decode(id_token, verify=False)
    user_id = user['email']
    user_type = user['custom:user_type']
    credit = int(user['custom:credits'])

    user_type = "Mentee"

    if user_type != "Mentee":
        return{
            "statusCode": 409,
            "body": json.dumps({
            "message": "Invalid user type. Only Aspiring Professionals may reserve chats."
            })
        }
    # ----------------------- End user validation ------------------------------

    chat_id = event["pathParameters"]["chatId"]

    session = Session()
    chat = session.query(Chat).get(chat_id)

    if chat != None:
        # check if user is in the list
        if user_id in chat.aspiring_professionals:
            i = chat.aspiring_professionals.index(user_id)
            chat.aspiring_professionals.pop(i)

            #check if we need to modify the status
            if chat.chat_status == ChatStatus.RESERVED:
                chat.chat_status = ChatStatus.ACTIVE

            session.commit()
            session.close()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "User {} has un-reserved Chat with ID {}".format(user_id, chat_id)
                })
            }
        else:
            session.close() # didn't even reserve this chat yet my dude
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "User {} has not reserved Chat with ID {}, cannot un-reserve".format(user_id, chat_id)
                })
            }

    else:
        session.close()

        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in Chats table".format(chat_id)
            })
        }
