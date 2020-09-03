import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from GetAllJobApplications import lambda_function as get_all

job_apps_db = []
context = ""

########################################################################
#                          GET ALL TEST CASES                          #
########################################################################
class TestJobApplicationsGetAll(unittest.TestCase):

    msg_status_code = "Expected status code {}, but returned {}"

    def test_getAll_200(self):
        event = {}
        event["queryStringParameters"] = {"userId": "id1",
                                           "jobId": "job1"} 
        event["body"] = None
        with mock.patch("GetAllJobApplications.lambda_function.Session") as mock_session:
            ret = get_all.handler(event, context)

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)