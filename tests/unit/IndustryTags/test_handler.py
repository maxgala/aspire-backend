import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from base import Session, row2dict
from Create import lambda_function as create
from DeleteById import lambda_function as delete
from GetAll import lambda_function as get_all
from GetById import lambda_function as get

tags_db = []


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
        tag = "tag1"
        with mock.patch("Create.lambda_function.Session") as mock_session:
            mock_add = mock_session.return_value.add
            mock_add.side_effect = tags_db.append(tag)
            ret = create.handler(apigw_create_event(tag), "")

        self.assertEqual(ret["statusCode"], 201, self.msg_status_code.format(201, ret["statusCode"]))
        self.assertTrue(tag in tags_db)

    def test_create_400(self):
        tag = ""
        with mock.patch("Create.lambda_function.Session") as mock_session:
            ret = create.handler(apigw_create_event(tag), "")

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
        search = "tag"
        fuzzy = "false"
        with mock.patch("GetAll.lambda_function.Session") as mock_session:
            ret = get_all.handler(apigw_getAll_event(search, fuzzy), "")

        # data = json.loads(ret["body"])
        # tags = [record["tag"] for record in data['industry_tags']]

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))

    def test_getAll_fuzzy_200(self):
        with mock.patch("GetAll.lambda_function.Session") as mock_session:
            ret = get_all.handler(apigw_getAll_event("tag", "true"), "")

        # data = json.loads(ret["body"])
        # tags = [record["tag"] for record in data['industry_tags']]

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

    def test_get_200(self):
        tag = "tag1"
        with mock.patch("GetById.lambda_function.Session") as mock_session:
            with mock.patch("GetById.lambda_function.row2dict") as mock_row2dict:
                mock_row2dict.return_value = {"tag": tag}
                ret = get.handler(apigw_get_event(tag), "")

        data = json.loads(ret["body"])

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        self.assertTrue(tag == data["tag"])

    def test_get_400(self):
        tag = ""
        with mock.patch("GetById.lambda_function.Session") as mock_session:
            ret = get.handler(apigw_get_event(""), "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))

    def test_get_404(self):
        tag = "tag4"
        with mock.patch("GetById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = get.handler(apigw_get_event(tag), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


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
        tag = "tag1"
        with mock.patch("DeleteById.lambda_function.Session") as mock_session:
            mock_delete = mock_session.return_value.delete
            mock_delete.side_effect = tags_db.remove(tag)
            ret = delete.handler(apigw_delete_event(tag), "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        self.assertTrue(tag not in tags_db)

    def test_delete_400(self):
        tag = ""
        with mock.patch("DeleteById.lambda_function.Session") as mock_session:
            ret = delete.handler(apigw_delete_event(tag), "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))

    def test_delete_404(self):
        tag = "tag1"
        with mock.patch("DeleteById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = delete.handler(apigw_delete_event(tag), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


if __name__ == "__main__":
    unittest.main(exit=False)
