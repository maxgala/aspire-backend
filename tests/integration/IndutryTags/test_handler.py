import sys
import os
import json
import pytest

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/IndustryTags" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from Create import lambda_function as create
from DeleteById import lambda_function as delete
from GetAll import lambda_function as get_all
from GetById import lambda_function as get


########################################################################
#                          CREATE TEST CASES                           #
########################################################################
@pytest.fixture()
def apigw_create_event():
    """ Generates API GW Event"""
    def _gen(tag):
        return {
            "body": '{"tag": "%s"}' % (tag)
        }

    return _gen

def test_create_201(apigw_create_event, mocker):
    ret = create.handler(apigw_create_event("tag1"), "")
    assert ret["statusCode"] == 201

    ret = create.handler(apigw_create_event("tag2"), "")
    assert ret["statusCode"] == 201

    ret = create.handler(apigw_create_event("tag3"), "")
    assert ret["statusCode"] == 201

    ret = create.handler(apigw_create_event("other tag"), "")
    assert ret["statusCode"] == 201

def test_create_400(apigw_create_event, mocker):
    ret = create.handler(apigw_create_event(""), "")

    assert ret["statusCode"] == 400


########################################################################
#                          GET ALL TEST CASES                          #
########################################################################
@pytest.fixture()
def apigw_getAll_event():
    """ Generates API GW Event"""
    def _gen(search, fuzzy):
        return {
            "body": '{}',
            "queryStringParameters": {"search": "%s" % (search), "fuzzy": "%s" % (fuzzy)}
        }

    return _gen

def test_getAll_200(apigw_getAll_event, mocker):
    ret = get_all.handler(apigw_getAll_event("tag", "false"), "")
    data = json.loads(ret["body"])
    tags = [record["tag"] for record in data['industry_tags']]

    assert ret["statusCode"] == 200
    assert "tag1" in tags
    assert "tag2" in tags
    assert "tag3" in tags

def test_getAll_fuzzy_200(apigw_getAll_event, mocker):
    ret = get_all.handler(apigw_getAll_event("tag", "true"), "")
    data = json.loads(ret["body"])
    tags = [record["tag"] for record in data['industry_tags']]

    assert ret["statusCode"] == 200
    assert "tag1" in tags
    assert "tag2" in tags
    assert "tag3" in tags
    assert "other tag" in tags


########################################################################
#                         GET BY ID TEST CASES                         #
########################################################################
@pytest.fixture()
def apigw_get_event():
    """ Generates API GW Event"""
    def _gen(tag):
        return {
            "body": '{}',
            "pathParameters": {"industryTagId": "%s" % (tag)}
        }

    return _gen

def test_get_200(apigw_get_event, mocker):
    ret = get.handler(apigw_get_event("tag1"), "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "tag1" == data["tag"]

def test_get_400(apigw_get_event, mocker):
    ret = get.handler(apigw_get_event(""), "")

    assert ret["statusCode"] == 400

def test_get_404(apigw_get_event, mocker):
    ret = get.handler(apigw_get_event("tag4"), "")

    assert ret["statusCode"] == 404


########################################################################
#                       DELETE BY ID TEST CASES                        #
########################################################################
@pytest.fixture()
def apigw_delete_event():
    """ Generates API GW Event"""
    def _gen(tag):
        return {
            "body": '{}',
            "pathParameters": {"industryTagId": "%s" % (tag)}
        }

    return _gen

def test_delete_200(apigw_delete_event, mocker):
    ret = delete.handler(apigw_delete_event("tag1"), "")
    assert ret["statusCode"] == 200

    ret = delete.handler(apigw_delete_event("tag2"), "")
    assert ret["statusCode"] == 200

    ret = delete.handler(apigw_delete_event("tag3"), "")
    assert ret["statusCode"] == 200

    ret = delete.handler(apigw_delete_event("other tag"), "")
    assert ret["statusCode"] == 200

def test_delete_400(apigw_delete_event, mocker):
    ret = delete.handler(apigw_delete_event(""), "")

    assert ret["statusCode"] == 400

def test_delete_404(apigw_delete_event, mocker):
    ret = delete.handler(apigw_delete_event("tag1"), "")
    assert ret["statusCode"] == 404

    ret = delete.handler(apigw_delete_event("tag2"), "")
    assert ret["statusCode"] == 404

    ret = delete.handler(apigw_delete_event("tag3"), "")
    assert ret["statusCode"] == 404

    ret = delete.handler(apigw_delete_event("other tag"), "")
    assert ret["statusCode"] == 404
