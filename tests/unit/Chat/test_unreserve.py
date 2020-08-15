import sys

sys.path.insert(0, "../../../src/lambda/Chat")
sys.path.insert(0, "../../../src/models/")

import json
import unittest
from unittest import mock

from UnreserveChatById import lambda_function as unreserve

import chat

context = ""

class TestReserveChatById(unittest.TestCase):
    # This is ignoring all auth, so needs to be updated once auth finalized.
    msg_status_code = "Expected status code{}, but returned {}"

    def test00_valid_unreserve(self):
        event = {}
        event["body"] = None

        chat_id = 10
        
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        
        with mock.patch("UnreserveChatById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            
            mock_chat = chat.Chat()
            mock_chat.chat_status = chat.ChatStatus.ACTIVE
            mock_chat.aspiring_professionals = [""]
            
            mock_get.return_value = mock_chat
            
            actual = unreserve.handler(event, context)
            
        expected = {"statusCode": 200, "body": json.dumps(
                {}
            )}

        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
    def test01_not_reserved(self):
        event = {}
        event["body"] = None

        chat_id = 10
        
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id        

        with mock.patch("UnreserveChatById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            
            mock_chat = chat.Chat()
            mock_chat.chat_status = chat.ChatStatus.ACTIVE
            mock_chat.aspiring_professionals = ["Henry"]
            
            mock_get.return_value = mock_chat
            
            actual = unreserve.handler(event, context)
            
        expected = {"statusCode": 400, "body": json.dumps(
                {}
            )}

        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
    def test02_invalid_id(self):
        event = {}
        event["body"] = None

        chat_id = -1
        
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id        

        with mock.patch("UnreserveChatById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            
            mock_get.return_value = None
            actual = unreserve.handler(event, context)
            
        expected = {"statusCode": 404, "body": json.dumps(
                {}
            )}

        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
if __name__ == "__main__":
    unittest.main(exit=False)
