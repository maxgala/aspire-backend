import sys

sys.path.insert(0, "../src/lambda/Chat")
sys.path.insert(0, "../src/models/")

import json
import unittest

from CreateChat import lambda_function as create
from DeleteChatById import lambda_function as delete
from EditChatById import lambda_function as edit
from GetAllChats import lambda_function as get_all
from GetChatById import lambda_function as get
from ReserveChatById import lambda_function as reserve
from UnreserveChatById import lambda_function as unreserve

import chat

context = ""

class TestCreateChat(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    msg_body = "Expected body {}, but returned {}"
    def test00_one_on_one(self):
        event = {}
        request = { "chat_type": 1,
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": []
                    }
        
        event["body"] = json.dumps(request)
        
        actual = create.handler(event, context)
        
        self.assertEqual(actual["statusCode"], 200, \
                         self.msg_status_code.format(200, \
                                                     actual["statusCode"]))

        
    def test01_one_on_four_no_date(self):
        event = {}
        request = { "chat_type": 2,
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": []
                    }

        event["body"] = json.dumps(request)
        actual = create.handler(event, context)
        expected = {"statusCode": 400, \
                    "body": {"message": "For a {} chat, date must be specified".format(chat.ChatType.ONE_ON_FOUR)
                    }}
        
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
        actual_body = actual["body"]
        assert (json.loads(actual_body) == expected["body"])

        event = {}
        request = { "chat_type": 2,
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": [],
                    "date": 10000
                    }
        
        event["body"] = json.dumps(request)
        actual = create.handler(event, context)

        expected = {"statusCode": 200, "body": request}
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
        
    def test03_mock_interview_no_date(self):
        event = {}
        request = { "chat_type": 3,
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": []
                    }
        event["body"] = json.dumps(request)
        
        actual = create.handler(event, context)
        expected = {"statusCode": 400, \
                    "body": {"message": "For a {} chat, date must be specified".format(chat.ChatType.MOCK_INTERVIEW)
                    }}
        
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

        actual_body = actual["body"]
        assert (json.loads(actual_body) == expected["body"])
    
    def test03_mock_interview_with_date(self):
        event = {}
        request = { "chat_type":3,
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": [],
                    "date": 10000
                    }
        event["body"] = json.dumps(request)
        
        actual = create.handler(event, context)

        expected = {"statusCode": 200, "body": request}
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

if __name__ == "__main__":
    unittest.main(exit=False)
