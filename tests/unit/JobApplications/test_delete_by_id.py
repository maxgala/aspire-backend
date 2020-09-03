import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from DeleteJobApplicationById import lambda_function as delete

job_apps_db = []
context = ""

# ########################################################################
# #                       DELETE BY ID TEST CASES                        #
# ########################################################################
def apigw_delete_event(id_param):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobAppId": "%s" % (id_param)}
    }

class TestJobApplicationDeleteById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_delete_200(self):
        id = "id_success"
        with mock.patch("DeleteJobApplicationById.lambda_function.Session") as mock_session:
            mock_delete = mock_session.return_value.delete
            if id in job_apps_db: mock_delete.side_effect = job_apps_db.remove(id)
            ret = delete.handler(apigw_delete_event(id), "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        self.assertTrue(id not in job_apps_db)

    def test_delete_404(self):
        id = "id_failure"
        with mock.patch("DeleteJobApplicationById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = delete.handler(apigw_delete_event(id), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)