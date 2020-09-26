import sys
import os
import json
import unittest
from unittest import mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))

from GetAll import lambda_function as get_all

tags_db = [
    "tag1",
    "tag2",
    "other tag"
]

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
        expected_tags = [
            {"tag": tags_db[0]},
            {"tag": tags_db[1]}
        ]
        with mock.patch("GetAll.lambda_function.Session") as mock_session:
            with mock.patch("GetAll.lambda_function.row2dict") as mock_row2dict:
                mock_row2dict.side_effect = expected_tags
                mock_query = mock_session.return_value.query
                mock_filter = mock_query.return_value.filter
                mock_all = mock_filter.return_value.all
                mock_all.return_value = expected_tags
                ret = get_all.handler(apigw_getAll_event(search, fuzzy), "")

        data = json.loads(ret["body"])
        tags = [record["tag"] for record in data['industry_tags']]

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        self.assertTrue(data['count'] == 2)
        self.assertTrue(tags_db[0] in tags)
        self.assertTrue(tags_db[1] in tags)

    def test_getAll_fuzzy_200(self):
        search = "tag"
        fuzzy = "true"
        expected_tags = [
            {"tag": tags_db[0]},
            {"tag": tags_db[1]},
            {"tag": tags_db[2]}
        ]
        with mock.patch("GetAll.lambda_function.Session") as mock_session:
            with mock.patch("GetAll.lambda_function.row2dict") as mock_row2dict:
                mock_row2dict.side_effect = expected_tags
                mock_query = mock_session.return_value.query
                mock_filter = mock_query.return_value.filter
                mock_all = mock_filter.return_value.all
                mock_all.return_value = expected_tags
                ret = get_all.handler(apigw_getAll_event(search, fuzzy), "")

        data = json.loads(ret["body"])
        tags = [record["tag"] for record in data['industry_tags']]

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        self.assertTrue(data['count'] == 3)
        self.assertTrue(tags_db[0] in tags)
        self.assertTrue(tags_db[1] in tags)
        self.assertTrue(tags_db[2] in tags)


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
