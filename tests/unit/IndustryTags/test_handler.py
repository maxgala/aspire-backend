import sys
import json
import unittest
from unittest import mock

sys.path.insert(0, "../../../src/lambda/IndustryTags")
sys.path.insert(0, "../../../src/models/")
# from base import Session
from Create import lambda_function as create
from DeleteById import lambda_function as delete
from GetAll import lambda_function as get_all
from GetById import lambda_function as get



########################################################################
#                          CREATE TEST CASES                           #
########################################################################
def apigw_create_event(tag):
    """ Generates Event"""
    return {
        "body": '{"tag": "%s"}' % (tag)
    }

class TestIndustryTagsCreate(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_create_201(self):
        with mock.patch("Create.lambda_function.Session") as mock_session:
            ret = create.handler(apigw_create_event("tag1"), "")

        self.assertEqual(ret["statusCode"], 201, self.msg_status_code.format(200, ret["statusCode"]))

    def test_create_400(self):
        with mock.patch("Create.lambda_function.Session") as mock_session:
            ret = create.handler(apigw_create_event(""), "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))


########################################################################
#                          GET ALL TEST CASES                          #
########################################################################
def apigw_getAll_event(search, fuzzy):
    """ Generates Event"""
    return {
        "body": '{}',
        "queryStringParameters": {"search": "%s" % (search), "fuzzy": "%s" % (fuzzy)}
    }

class TestIndustryTagsGetAll(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_getAll_200(self):
        with mock.patch("GetAll.lambda_function.Session") as mock_session:
            ret = get_all.handler(apigw_getAll_event("tag", "false"), "")

        data = json.loads(ret["body"])
        tags = [record["tag"] for record in data['industry_tags']]

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

    def test_getAll_fuzzy_200(self):
        with mock.patch("GetAll.lambda_function.Session") as mock_session:
            ret = get_all.handler(apigw_getAll_event("tag", "true"), "")

        data = json.loads(ret["body"])
        tags = [record["tag"] for record in data['industry_tags']]

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))


# ########################################################################
# #                         GET BY ID TEST CASES                         #
# ########################################################################
def apigw_get_event(tag):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"industryTagId": "%s" % (tag)}
    }

class TestIndustryTagsGetById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    # def test_get_200(self):
    #     with mock.patch("GetById.lambda_function.Session") as mock_session:
    #         ret = get.handler(apigw_get_event("tag1"), "")
    #     data = json.loads(ret["body"])

    #     self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
    #     # assert "tag1" == data["tag"]

    def test_get_400(self):
        with mock.patch("GetById.lambda_function.Session") as mock_session:
            ret = get.handler(apigw_get_event(""), "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))

    # def test_get_404(self):
    #     with mock.patch("GetById.lambda_function.Session") as mock_session:
    #         with mock.patch("GetById.lambda_function.Query") as mock_session:
    #         mock_session.return_value = ""
    #         ret = get.handler(apigw_get_event("tag4"), "")

    #     self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


########################################################################
#                       DELETE BY ID TEST CASES                        #
########################################################################
def apigw_delete_event(tag):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"industryTagId": "%s" % (tag)}
    }

class TestIndustryTagsDeleteById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_delete_200(self):
        with mock.patch("DeleteById.lambda_function.Session") as mock_session:
            ret = delete.handler(apigw_delete_event("tag1"), "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

    def test_delete_400(self):
        with mock.patch("DeleteById.lambda_function.Session") as mock_session:
            ret = delete.handler(apigw_delete_event(""), "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))

    def test_delete_404(self):
        mock_query = mock.Mock()
        mock_query.get = mock.Mock(return_value="")
        mock.patch("DeleteById.lambda_function.Query", mock_query)
        # with mock.patch("DeleteById.lambda_function.Session") as mock_session:
        ret = delete.handler(apigw_delete_event("tag1"), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))

if __name__ == "__main__":
    unittest.main(exit=False)
