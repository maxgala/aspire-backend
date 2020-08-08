import sys

sys.path.insert(0, "../src/lambda/Chat")
sys.path.insert(0, "../src/models/")

import json
import unittest

from CreateChat import lambda_function as create
from DeleteChatById import lambda_function as delete

import chat
context = ""

class TestDeleteChatById(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    
    def test01_valid_id(self):
        event = {}
        request = { "chat_type": 1,
                    "description": "meow meow meow",
                    "senior_executive": "larry@gmail.com",
                    "aspiring_professionals": []
                    }
        
        event["body"] = json.dumps(request)
        chat = create.handler(event, context)
        chat_id = json.loads(chat["body"])["chat_id"]
        
        event = {}
        event["body"] = json.dumps({})
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        actual = delete.handler(event, context)
        
        expected = {"statusCode": 200, "body": json.dumps({
                "message": "Chat Row with ID {} deleted".format(chat_id)
            })}
        
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))

    def test01_invalid_id(self):
        chat_id = -1
        event = {}
        event["body"] = json.dumps({})
        event["pathParameters"] = {}
        event["pathParameters"]["chatId"] = chat_id
        actual = delete.handler(event, context)
        
        expected = {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID {} not found in Chats table".format(chat_id)
            })
        }
        
        self.assertEqual(actual["statusCode"], expected["statusCode"], \
                         self.msg_status_code.format(expected["statusCode"], \
                                                     actual["statusCode"]))    
        
if __name__ == "__main__":
    unittest.main(exit=False)
