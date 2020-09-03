import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from CreateJobApplication import lambda_function as create

job_apps_db = []
context = ""

########################################################################
#                          CREATE TEST CASES                           #
########################################################################
class TestIndustryTagsCreate(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_create_201(self):
        event = {}
        request = {
            "job_id": "2",
            "job_application_status": "OFFER_ACCEPT",
            "email": "testcreate@jobapplication.com",
            "resumes": "path/to/resume",
            "cover_letters": "path/to/coverletter"
            }
        event["body"] = json.dumps(request)    

        with mock.patch("CreateJobApplication.lambda_function.Session") as mock_session:
            mock_delete = mock_session.return_value.add
            mock_delete.side_effect = job_apps_db.append(request)
            ret = create.handler(event, context)

        self.assertEqual(ret["statusCode"], 201, self.msg_status_code.format(201, ret["statusCode"]))
        self.assertTrue(request in job_apps_db)


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)