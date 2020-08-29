import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict

from DeleteJobById import lambda_function as delete

context = ""

def apigw_delete_event(jobid):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobId": jobid}
    }

class TestDeleteJobById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"
    body_status_code = "Expected body code{}, but returned {}"
    
    def test_delete_404(self):
        job_id = 1
        with mock.patch("DeleteJobById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = delete.handler(apigw_delete_event(job_id), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))

    def test_delete_200(self):
        job_id = 1
        with mock.patch("DeleteJobById.lambda_function.Session") as mock_session:
            ret = delete.handler(apigw_delete_event(job_id), "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

    def test_delete_409(self):
        job_id = 1
        with mock.patch("DeleteJobById.lambda_function.Session") as mock_session:
            
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = mock.Mock(job_applications = ["1"])
            ret = delete.handler(apigw_delete_event(job_id), "")

        self.assertEqual(ret["statusCode"], 409, self.msg_status_code.format(409, ret["statusCode"]))
    

if __name__ == "__main__":
    unittest.main(exit=False)