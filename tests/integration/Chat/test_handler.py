import sys
import os
import json
import pytest

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Chat/" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
import chat
from CreateChat import lambda_function as create
from DeleteChatById import lambda_function as delete
from GetAllChats import lambda_function as get_all
from GetChatById import lambda_function as get
from EditChatById import lambda_function as update
from ReserveChatById import lambda_function as reserve
from UnreserveChatById import lambda_function as unreserve

context = ""

class TestChat:
    def test_00_integration_one_on_one_no_date(self):
        result = get_all.handler({}, context)
        
        result_body = json.loads(result["body"])
        count = int(result_body["count"])
        
        # create a one-on-one with no date
        event = {}
        event["body"] = json.dumps({
            "chat_type": 1,
            "senior_executive": "larry@gmail.com",
            "aspiring_professionals": []
            })

        result = create.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["chat_status"] == "ChatStatus.PENDING"
        assert result_body["chat_type"] == "ChatType.ONE_ON_ONE"
        assert result_body["senior_executive"] == "larry@gmail.com"
        assert result_body["aspiring_professionals"] == '[]'

        chat_id = result_body["chat_id"]

        # try to reserve the chat, but status is pending
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"]  = chat_id
        
        result = reserve.handler(event, context)
        assert result["statusCode"] == 409
        
        result_body = json.loads(result["body"])
        msg = "Chat with ID {} cannot be reserved, chat status is {}".format(chat_id, chat.ChatStatus.PENDING)
        assert result_body["message"] == msg
        # edit the chat to status active
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"]  = chat_id
        event["body"] = json.dumps({
                "chat_status": 2
            })
        
        result = update.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
              "Updated Chat Row, with ID {}".format(
                   chat_id
                )

        # try to reserve the chat, as status is active
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"]= chat_id
        
        result = reserve.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  "Reserved Chat with ID {} for User {}".format(chat_id, '')

        # get the chat to see new status
        result = get.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["chat_status"] == "ChatStatus.RESERVED"
        assert result_body["chat_type"] == "ChatType.ONE_ON_ONE"
        assert result_body["senior_executive"] == "larry@gmail.com"
        assert result_body["aspiring_professionals"] == "['']"

        # unreserve the chat
        
        result = unreserve.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "User {} has un-reserved Chat with ID {}".format(
                   '', chat_id
                )
        
        # get the chat to see new status
        
        result = get.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["chat_status"] == "ChatStatus.ACTIVE"
        assert result_body["chat_type"] == "ChatType.ONE_ON_ONE"
        assert result_body["senior_executive"] == "larry@gmail.com"
        assert result_body["aspiring_professionals"] == "[]"

        # get all chats

        result = get_all.handler({}, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["count"] == (count + 1)
        
        # delete the chat
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        
        result = delete.handler(event, context)
        assert result["statusCode"] == 200

        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "Chat Row with ID {} deleted".format(
                   chat_id
                )
        
    def test_01_integration_chat_not_in_table(self):
        chat_id = -1
        
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = -1

        
        # get chat doesnt exist  
        result = get.handler(event, context)
        assert result["statusCode"] == 404
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
                "ID {} not found in Chats table".format(
                    chat_id
                )
        
        # edit a chat which doesn't exist
        event = {}
        event["body"] = json.dumps({
                "chat_status": 1
            })
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = -1
        result = update.handler(event, context)
        assert result["statusCode"] == 404
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
                "ID {} not found in Chats table".format(
                    chat_id
                )

        # delete
        result = delete.handler(event, context)
        assert result["statusCode"] == 404
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
                "ID {} not found in Chats table".format(
                    chat_id
                )
        
        # reserve
        result = reserve.handler(event, context)
        assert result["statusCode"] == 404
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
                "ID {} not found in Chats table".format(
                    chat_id
                )
        
        # unreserve
        result = unreserve.handler(event, context)
        assert result["statusCode"] == 404
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
                "ID {} not found in Chats table".format(
                    chat_id
                )
            
    def test_02_integration_FOUR_ON_ONE(self):
        # create a four-on-one with no date
        event = {}
        event["body"] = json.dumps({
            "chat_type": 2,
            "senior_executive": "larry@gmail.com",
            "aspiring_professionals": []
            })

        result = create.handler(event, context)
        assert result["statusCode"] == 400
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "For a {} chat, date must be specified".format(
                   chat.ChatType.ONE_ON_FOUR
                )

        ## with date
        event = {}
        event["body"] = json.dumps({
            "chat_type": 2,
            "senior_executive": "larry@gmail.com",
            "date": 1000,
            "aspiring_professionals": []
        })
        
        result = create.handler(event, context)
        assert result["statusCode"] == 200

        result_body = json.loads(result["body"])
        assert result_body["chat_status"] == "ChatStatus.PENDING"
        assert result_body["chat_type"] == "ChatType.ONE_ON_FOUR"
        assert result_body["senior_executive"] == "larry@gmail.com"
        assert result_body["aspiring_professionals"] == "[]"

        chat_id = result_body["chat_id"]

        # edit the chat to status active
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"]  = chat_id
        event["body"] = json.dumps({
                "chat_status": 2
            })
        
        result = update.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
              "Updated Chat Row, with ID {}".format(
                   chat_id
                )

        # unreserve the chat without having reserved
        result = unreserve.handler(event, context)
        assert result["statusCode"] == 400
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "User {} has not reserved Chat with ID {}, cannot un-reserve".format(
                   '', chat_id
                )
        
        # reserve the chat, as status is active
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"]= chat_id
        
        result = reserve.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "Reserved Chat with ID {} for User {}".format(
                   chat_id, ''
                )

        # get the chat to see new status
        result = get.handler(event, context)
        assert result["statusCode"] == 200
        
        result_body = json.loads(result["body"])
        assert result_body["chat_status"] == "ChatStatus.ACTIVE"
        assert result_body["chat_type"] == "ChatType.ONE_ON_FOUR"
        assert result_body["senior_executive"] == "larry@gmail.com"
        assert result_body["aspiring_professionals"] == "['']"

        # try to reserve again
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"]= chat_id
        
        result = reserve.handler(event, context)
        assert result["statusCode"] == 409
        
        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "User {} has already reserved Chat with ID {}".format(
                   '', chat_id
                )

        # delete the chat
        event = {}
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        
        result = delete.handler(event, context)
        assert result["statusCode"] == 200

        result_body = json.loads(result["body"])
        assert result_body["message"] ==  \
               "Chat Row with ID {} deleted".format(
                   chat_id
                )
