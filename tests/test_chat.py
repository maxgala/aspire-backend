# import sys
# import os

# CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, "%s/../src/lambda/Chat" % CURRENT_DIRECTORY)
# sys.path.insert(0, "%s/../src/models/" % CURRENT_DIRECTORY)
# # sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
# # sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))

# import json
# import unittest

# from CreateChat import lambda_function as create
# from DeleteChatById import lambda_function as delete
# from EditChatById import lambda_function as edit
# from GetAllChats import lambda_function as get_all
# from GetChatById import lambda_function as get
# from ReserveChatById import lambda_function as reserve
# from UnreserveChatById import lambda_function as unreserve


# context = ""

# class TestCreateChat(unittest.TestCase):
#     self.msg_status_code = "Expected status code{}, but returned {}"
#     self.body_status_code = "Expected body code{}, but returned {}"
#     def test00_one_on_one(self):
#         event = {}
#         request = { "chat_type": 1,
#                     "senior_executive": "larry@gmail.com",
#                     "aspiring_professionals": []
#                     }

#         event["body"] = request
#         actual = create.handler(event, context)

#         expected = {"statusCode": 200, "body": request}
#         self.assertEqual(actual["statusCode"], expected["statusCode"], self.msg_status_code.format(expected["statusCode"], \
#                                                                                   actual["statusCode"]))
#         self.assertEqual(actual["body"], expected["body"], self.msg_body_code.format(actual["body"], expected["body"]))

#     def test01_four_on_one_no_date(self):
#         pass
#     def test02_four_on_one_with_date(self):
#         pass
#     def test03_mock_interview(self):
#         pass


# if __name__ == "__main__":
#     unittest.main(exit=False)
