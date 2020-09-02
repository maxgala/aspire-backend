import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from CreateJob import lambda_function as create

context = ""


class TestCreateJob(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    msg_body_code = "Expected body message{}, but returned {}"
    ids_created = []
    def test_createJob(self):
        event = {}
        request = {
                "title":"Software Developer",
                "company":"My-Company",
                "region":"ON",
                "city":"Waterloo",
                "country":"Canada",
                "job_type": "BOARD_POSITION",
                "description":"XYZ",
                "requirements":"XYZ",
                "job_tags":["SOFTWARE","FINANCE"],
                "salary":40,
                "deadline":1593718782,
                "email": "test@email.xyz",
                "family_name": "Suleman",
                "given_name": "S"
            }
        event["body"] = json.dumps(request)
        actual = {}
        
        with mock.patch("CreateJob.lambda_function.Session") as mock_session:
            actual = create.handler(event, context)
        
        data = json.loads(actual["body"])
        self.assertEqual(actual["statusCode"], 201, \
                             self.msg_status_code.format(201, \
                                                         actual["statusCode"]))
        self.assertTrue(data["message"], "Created Job Row")
    

if __name__ == "__main__":
    unittest.main(exit=False)