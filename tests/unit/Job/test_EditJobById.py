import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict

from EditJobById import lambda_function as edit

context = ""

def apigw_edit_event(jobid):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobId": jobid}
    }

class TestEditJobById(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    body_status_code = "Expected body code{}, but returned {}"
    def test01_invalid_id(self):
        job_id = 1
        with mock.patch("EditJobById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_edit = mock_query.return_value.get
            mock_edit.return_value = None
            ret = edit.handler(apigw_edit_event(job_id), context)

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))
    
    def test02_valid_id(self):
        job_id = 100
        
        with mock.patch("EditJobById.lambda_function.Session") as mock_session:
            ret = edit.handler(apigw_edit_event(job_id), "")

        data = json.loads(ret["body"])
        
        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
    

if __name__ == "__main__":
    unittest.main(exit=False)