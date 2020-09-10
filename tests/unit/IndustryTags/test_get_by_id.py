import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))

from GetById import lambda_function as get

tags_db = [
    "tag1"
]

########################################################################
#                         GET BY ID TEST CASES                         #
########################################################################
def apigw_get_event(tag):
    """ Generates Event"""
    return {
        "body": '{}',
        "pathParameters": {"industryTagId": "%s" % (tag)}
    }

class TestIndustryTagsGetById(unittest.TestCase):
    msg_status_code = "Expected status code {}, but returned {}"

    def test_get_200(self):
        tag = tags_db[0]
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
            ret = get.handler(apigw_get_event(tag), "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))

    def test_get_404(self):
        tag = "nonexistent tag"
        with mock.patch("GetById.lambda_function.Session") as mock_session:
            mock_query = mock_session.return_value.query
            mock_get = mock_query.return_value.get
            mock_get.return_value = None
            ret = get.handler(apigw_get_event(tag), "")

        self.assertEqual(ret["statusCode"], 404, self.msg_status_code.format(404, ret["statusCode"]))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
