import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict

from GetAllJobs import lambda_function as get_all

context = ""

class TestGetAllJobs(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    body_status_code = "Expected body code{}, but returned {}"
    def test_200(self):
        event={}
        event["queryStringParameters"] = ""
        with mock.patch("GetAllJobs.lambda_function.Session") as mock_session:
            actual = get_all.handler(event, context)
        expected = {"statusCode": 200}
        self.assertEqual(actual["statusCode"], expected["statusCode"], self.msg_status_code.format(expected["statusCode"], \
                                                                                  actual["statusCode"]))
        #self.assertEqual(actual["body"], expected["body"], self.msg_body_code.format(actual["body"], expected["body"])
    

if __name__ == "__main__":
    unittest.main(exit=False)