import sys
import os
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))

from Create import lambda_function as create

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


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
