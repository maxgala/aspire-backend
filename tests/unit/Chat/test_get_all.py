import sys

sys.path.insert(0, "../../../src/lambda/Chat")
sys.path.insert(0, "../../../src/models/")

import json
import unittest
from unittest import mock
from sqlalchemy.orm.query import Query

from GetAllChats import lambda_function as get_all

import chat
context = ""

class TestGetAllChats(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"

    def test00_valid_id(self):
        event = {}
        event["body"] = None

        chat_id = 10
        
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        
        with mock.patch("GetAllChats.lambda_function.Session") as mock_session:
            actual = get_all.handler(event, context)
            
        expected = {"statusCode": 200, "body": json.dumps(
                {}
            )}

        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

if __name__ == "__main__":
    unittest.main(exit=False)
