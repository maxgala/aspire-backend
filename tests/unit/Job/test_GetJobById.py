import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict

from GetJobById import lambda_function as get
from CreateJob import lambda_function as create

context = ""

def apigw_get_event(jobid):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobId": jobid}
    }

class TestGetJobById(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    body_status_code = "Expected body code{}, but returned {}"
    def test01_invalid_id(self):
        job_id = 1
        with mock.patch("GetJobById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = get.handler(apigw_get_event(job_id), context)

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))
    
    def test02_valid_id(self):
        job_id = 100
        
        with mock.patch("GetJobById.lambda_function.Session") as mock_session:
            with mock.patch("GetJobById.lambda_function.row2dict") as mock_row2dict:
                mock_query = mock_session.return_value.query
                mock_get = mock_query.return_value.get
                #mock_job_applications = mock_get.return_value.job_applications
                #mock_job_applications.return_value = ["1"]
                mock_row2dict.return_value = {"job_id": job_id}
                #print(mock_row2dict.return_value)
                ret = get.handler(apigw_get_event(job_id), "")

        data = json.loads(ret["body"])
        print(data)
        
        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

        #self.assertEqual(actual["body"], expected["body"], self.msg_body_code.format(actual["body"], expected["body"])
    

if __name__ == "__main__":
    unittest.main(exit=False)