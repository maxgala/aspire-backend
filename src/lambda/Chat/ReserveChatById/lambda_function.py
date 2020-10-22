import json
from chat import *
from base import Session, MutableList
import boto3
import jwt
from send_email import send_email, send_email_Outlook, Identity, build_cal_event
from datetime import datetime

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
    # user is mentee

    chat_id = event["pathParameters"]["chatId"]

    session = Session()
    chat = session.query(Chat).get(chat_id)

    if chat != None:
        credit_cost = credit_mapping[chat.chat_type]
        sufficient_credits = credit >= credit_cost

        if not sufficient_credits:
            session.close()
            return {
                "statusCode": 409,
                "body": json.dumps({
                "message": "Insufficient credits, need {} but have {}".format(credit_cost, credit)
                })
            }


        if chat.chat_status != ChatStatus.ACTIVE:
            # cannot reserve this chat, it is not active
            session.close()
            return {
                "statusCode": 409,
                "body": json.dumps({
                "message": "Chat with ID {} cannot be reserved, chat status is {}".format(chat.chat_id, chat.chat_status)
                })
            }

        # ----------------------- all ok to go ahead and reserve ---------------------------

        response = client.update_user_attributes(
            UserAttributes=[
                {
                    'Name': 'custom:credits',
                    'Value': str(int(credit) - credit_cost)
                },
            ],
            AccessToken=access_token
        )

        # credits updated
        if chat.aspiring_professionals == None:
            chat.aspiring_professionals = MutableList.coerce(chat.aspiring_professionals, [user_id])
            # create a new entry
        else:
             # check if user has already reserved this chat
            if user_id in chat.aspiring_professionals:
                session.close()
                return {"statusCode": 409,
                        "body": json.dumps({
                        "message": "User {} has already reserved Chat with ID {}".format(user_id, chat_id)
                        })
                    }
            else:
                #modify existing entry
                chat.aspiring_professionals.append(user_id)

        # check if chat is reserved
        if chat.chat_type == ChatType.ONE_ON_ONE:
            # one on one, reserve chat
            chat.chat_status = ChatStatus.RESERVED #reserved
        elif chat.chat_type == ChatType.FOUR_ON_ONE: # one on four
            num_mentees = len(chat.aspiring_professionals)
            if num_mentees == 4:
                chat.chat_status = ChatStatus.RESERVED # reserved

        session.commit()
        session.close()

        # --- Send emails ---
        recipients = []
        recipients.append(Identity("Recipient name", user_id))
        if chat.chat_type == ChatType.ONE_ON_ONE or len(chat.aspiring_professionals) == 1:
            recipients.append(Identity("Recipient name", chat.senior_executive))

        ## FIXME change sender name
        sender = Identity("Sender name", "naba@poketapp.com")
        subject = "Hello world"
        body = "lorem ipsum dolor sit amet"
        outlookrec= []
        AllOtherrec= []
        numRecepients= len(recipients)

        i= 0
        while i < numRecepients:
            if "outlook" in recipients[i].email:
                outlookrec.append(recipients[i])
            else:
                AllOtherrec.append(recipients[i])
            i += 1

        subject = "Hello world"
        body = "lorem ipsum dolor sit amet"

        dtstart = datetime(2020, 9, 9, 22, 15, 0)
        dtend = datetime(2020, 9, 9, 22, 30, 0)

        ics = build_cal_event("cat_screams", "He is rlly homgry", sender, recipients, dtstart, dtend)

        with open("/tmp/event.ics", 'w') as f:
            f.write(ics)

        if len(AllOtherrec) > 0:
            send_email(sender, AllOtherrec, subject, body, ics)
        if len(outlookrec) > 0:
            send_email_Outlook(sender, outlookrec, subject, body, ics)


        return {
            "statusCode": 200,
            "body": json.dumps({
            "message": "Reserved Chat with ID {} for User {}".format(chat_id, user_id)
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
