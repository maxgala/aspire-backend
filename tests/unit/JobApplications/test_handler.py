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
from DeleteJobApplicationById import lambda_function as delete
from GetAllJobApplications import lambda_function as get_all
from GetJobApplicationById import lambda_function as get
from EditJobApplicationById import lambda_function as update


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