import sys
import os
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))

from DeleteById import lambda_function as delete

tags_db = [
    "tag1"
]

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
    unittest.main(verbosity=2, exit=False)
