import sys

sys.path.insert(0, "../../../src/lambda/Chat")
sys.path.insert(0, "../../../src/models/")

import json
import unittest
from unittest import mock

from EditChatById import lambda_function as update

import chat

context = ""

class TestEditChatById(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"

    def test00_valid_id(self):
        event = {}
        event["body"] = None
        event["body"] = json.dumps({
            "chat_status": 2
        })
        chat_id = 10
        
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        
        with mock.patch("EditChatById.lambda_function.Session") as mock_session:
            actual = update.handler(event, context)
            
        expected = {"statusCode": 200, "body": json.dumps(
                {}
            )}

        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
    def test01_invalid_id(self):
        event = {}
        event["body"] = None

        chat_id = -1
        
        event["pathParameters"] = {}
        event["body"] = json.dumps({
            "chat_status": 2
        })
        event["pathParameters"]["chatId"] = chat_id
        
        with mock.patch("EditChatById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            actual = update.handler(event, context)


            
        expected = {"statusCode": 404, "body": json.dumps(
                {"message": "ID {} not found in Chats table".format(chat_id)}
            )}

        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

if __name__ == "__main__":
    unittest.main(exit=False)
