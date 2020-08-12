import sys

sys.path.insert(0, "../../../src/lambda/Chat")
sys.path.insert(0, "../../../src/models/")

import json
import unittest
from unittest import mock

from CreateChat import lambda_function as create

import chat
from base import Session

context = ""

class TestCreateChat(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    ids_created = []

    
    def test00_one_on_one(self):
        event = {}
        request = { "chat_type": 1,
                    "description": "meow meow meow",
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": []
                    }
        
        event["body"] = json.dumps(request)
        actual = {}
        
        with mock.patch("CreateChat.lambda_function.Session") as mock_session:
            actual = create.handler(event, context)
            
        self.assertEqual(actual["statusCode"], 200, \
                             self.msg_status_code.format(200, \
                                                         actual["statusCode"]))
        self.ids_created.append(json.loads(actual["body"])["chat_id"])
        
    def test01_one_on_four_no_date(self):
        event = {}
        request = { "chat_type": 2,
                    "senior_executive": "larry@gmail.com",
                    "description": "meow meow meow",
                    "aspiring_professionals": []
                    }

        event["body"] = json.dumps(request)
        
        with mock.patch("CreateChat.lambda_function.Session") as mock_session:
            actual = create.handler(event, context)

        expected = {"statusCode": 400, \
                    "body": {"message": "For a {} chat, date must be specified".format(chat.ChatType.ONE_ON_FOUR)
                    }}
        
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))
        actual_body = actual["body"]
        assert (json.loads(actual_body) == expected["body"])

    def test02_one_on_four_with_date(self):
        event = {}
        request = { "chat_type": 2,
                    "senior_executive": "larry@gmail.com",
                    "description": "meow meow meow",
                    "aspiring_professionals": [],
                    "date": 10000
                    }
        
        event["body"] = json.dumps(request)
        with mock.patch("CreateChat.lambda_function.Session") as mock_session:
            actual = create.handler(event, context)

        expected = {"statusCode": 200, "body": request}
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

        self.ids_created.append(json.loads(actual["body"])["chat_id"])
        
    def test03_mock_interview_no_date(self):
        event = {}
        request = { "chat_type": 3,
                    "senior_executive": "larry@gmail.com",
                    "description": "meow meow meow",
                    "aspiring_professionals": []
                    }
        event["body"] = json.dumps(request)
        
        with mock.patch("CreateChat.lambda_function.Session") as mock_session:
            actual = create.handler(event, context)
            
        expected = {"statusCode": 400, \
                    "body": {"message": "For a {} chat, date must be specified".format(chat.ChatType.MOCK_INTERVIEW)
                    }}
        
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

        actual_body = actual["body"]
        assert (json.loads(actual_body) == expected["body"])
    
    def test04_mock_interview_with_date(self):
        event = {}
        request = { "chat_type":3,
                    "senior_executive": "larry@gmail.com",
                    "description": "meow meow meow",
                    "aspiring_professionals": [],
                    "date": 10000
                    }
        event["body"] = json.dumps(request)
        
        with mock.patch("CreateChat.lambda_function.Session") as mock_session:
            actual = create.handler(event, context)

        expected = {"statusCode": 200, "body": request}
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

        self.ids_created.append(json.loads(actual["body"])["chat_id"])
   
        
if __name__ == "__main__":
    unittest.main(exit=False)
