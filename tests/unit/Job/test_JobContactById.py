import sys
import os
import json
import unittest
from unittest import mock


CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict

from JobContactById import lambda_function as contact

context = ""

def apigw_contact_event(jobid):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobId": jobid},
        "headers":{"Authorization": "Bearer, 123", }
    }

def apigw_contact_no_auth_event(jobid):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"jobId": jobid},
    }

class TestJobContactById(unittest.TestCase):
    msg_status_code = "Expected status code{}, but returned {}"
    body_status_code = "Expected body code{}, but returned {}"
    
    def test01_invalid_id(self):
        job_id = 1
        with mock.patch("JobContactById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = contact.handler(apigw_contact_event(job_id), context)

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))
    
    ### Need to work on this
    def test02_no_auth_header(self):
        job_id = 100
        
        with mock.patch("JobContactById.lambda_function.Session") as mock_session:
            ret = contact.handler(apigw_contact_no_auth_event(job_id), "")

        data = json.loads(ret["body"])
        
        self.assertEqual(ret["statusCode"], 401, self.msg_status_code.format(401, ret["statusCode"]))
    
    def test03_apply_before(self):
        job_id = 100
        
        with mock.patch("JobContactById.lambda_function.Session") as mock_session:
            with mock.patch("JobContactById.lambda_function.client") as mock_client:
                mock_getuser = mock_client.return_value.get_user
                mock_getuser.return_value = "123"
                ret = contact.handler(apigw_contact_event(job_id), "")

        data = json.loads(ret["body"])
        print(data)
        
        self.assertEqual(ret["statusCode"], 428, self.msg_status_code.format(428, ret["statusCode"]))
    
    def test04_not_enough_credits(self):
        job_id = 100
        
        with mock.patch("JobContactById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_app_id = mock_get.return_value.job_applications
            mock_get.return_value = mock.Mock(job_applications = [mock.Mock(applicant_id = "mock@email.com")], people_contacted = 3)
            with mock.patch("JobContactById.lambda_function.client") as mock_client:
                mock_client.get_user = mock.MagicMock(return_value = {"UserAttributes":[{"Name":"email","Value":"mock@email.com"},{"Name":"custom:credits","Value":4}]})
                ret = contact.handler(apigw_contact_event(job_id), "")

        data = json.loads(ret["body"])
        print(data)
        
        self.assertEqual(ret["statusCode"], 402, self.msg_status_code.format(402, ret["statusCode"]))
    
    def test05_success(self):
        job_id = 100
        
        with mock.patch("JobContactById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_app_id = mock_get.return_value.job_applications
            mock_get.return_value = mock.Mock(job_applications = [mock.Mock(applicant_id = "mock@email.com")], people_contacted = 3,posted_by = "me", poster_given_name ="me",poster_family_name ="me" )
            with mock.patch("JobContactById.lambda_function.client") as mock_client:
                mock_client.get_user = mock.MagicMock(return_value = {"UserAttributes":[{"Name":"email","Value":"mock@email.com"},{"Name":"custom:credits","Value":50}]})
                ret = contact.handler(apigw_contact_event(job_id), "")

        data = json.loads(ret["body"])
        print(data)
        
        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        

if __name__ == "__main__":
    unittest.main(exit=False)