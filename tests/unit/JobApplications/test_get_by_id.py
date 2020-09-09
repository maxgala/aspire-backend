import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from GetJobApplicationById import lambda_function as get

job_apps_db = []
context = ""

# # ########################################################################
# # #                         GET BY ID TEST CASES                         #
# # ########################################################################
def apigw_get_event(id_param):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobAppId": "%s" % (id_param)}
    }

class TestJobApplicationGetById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_get_200(self):

        with mock.patch("GetJobApplicationById.lambda_function.Session") as mock_session:
            with mock.patch("GetJobApplicationById.lambda_function.row2dict") as mock_row2dict:
                mock_query = mock_session.return_value.query
                mock_get = mock_query.return_value.get
                mock_row2dict.return_value = {"jobAppId": "id_success"}
                ret = get.handler(apigw_get_event("id_success"), "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

    def test_get_404(self):
        id = "id_failure"
        with mock.patch("GetJobApplicationById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = get.handler(apigw_get_event(id), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)