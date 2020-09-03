import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from EditJobApplicationById import lambda_function as update

job_apps_db = []
context = ""

# # ########################################################################
# # #                         EDIT BY ID TEST CASES                         #
# # ########################################################################
def apigw_update_event(id_param):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobAppId": "%s" % (id_param)}
    }

class TestJobApplicationEditById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_edit_200(self):
        id = "id_success"
        with mock.patch("EditJobApplicationById.lambda_function.Session") as mock_session:
            ret = update.handler(apigw_update_event(id), "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

    def test_edit_404(self):
        id = "id_failure"
        with mock.patch("EditJobApplicationById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = update.handler(apigw_update_event(id), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)