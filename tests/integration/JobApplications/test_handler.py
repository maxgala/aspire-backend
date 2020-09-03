import sys
import os
import json
import pytest

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from CreateJobApplication import lambda_function as create
from DeleteJobApplicationById import lambda_function as delete
from GetAllJobApplications import lambda_function as get_all
from GetJobApplicationById import lambda_function as get
from EditJobApplicationById import lambda_function as update

context = ""
ids_created = []

########################################################################
#                          CREATE TEST CASES                           #
########################################################################
@pytest.fixture()
def apigw_create_event():
    """ Generates API GW Event"""
    def _gen(email):
        return {
            "job_id": "2",
            "job_application_status": "OFFER_ACCEPT",
            "email": "%s" % (email),
            "resumes": "path/to/resume",
            "cover_letters": "path/to/coverletter"
        }
    return _gen

def test_create_201(apigw_create_event):
    event = {}

    request = apigw_create_event("test1@email.com")
    event["body"] = json.dumps(request)
    ret = create.handler(event, context)
    assert ret["statusCode"] == 201
    ret_body = json.loads(ret["body"])
    ids_created.append(ret_body["job_application_id"])

# ########################################################################
# #                          GET ALL TEST CASES                          #
# ########################################################################
@pytest.fixture()
def apigw_getAll_event():
    """ Generates API GW Event"""
    def _gen(jobId, userId):
        return {
            "body": '{}',
            "queryStringParameters": {"jobId": "%s" % (jobId), "userId": "%s" % (userId)}
        }

    return _gen

def test_getAll_200(apigw_getAll_event):
    ret = get_all.handler(apigw_getAll_event("", "test1@email.com"), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200

    ret = get_all.handler(apigw_getAll_event("2", "test1@email.com"), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200

    
    ret = get_all.handler(apigw_getAll_event("2",""), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200

    
    ret = get_all.handler(apigw_getAll_event("",""), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200


# ########################################################################
# #                         GET BY ID TEST CASES                         #
# ########################################################################
@pytest.fixture()
def apigw_getId_event():
    """ Generates API GW Event"""
    def _gen(jobAppId):
        return {
            "body": '{}',
            "pathParameters": {"jobAppId": "%s" % (jobAppId)}
        }

    return _gen

def test_getId_200(apigw_getId_event):
    ret = get.handler(apigw_getId_event("100"), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200

def test_getId_404(apigw_getId_event):
    ret = get.handler(apigw_getId_event("-1"), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 404

########################################################################
#                       UPDATE BY ID TEST CASES                        #
########################################################################
@pytest.fixture()
def apigw_updateId_event():
    """ Generates API GW Event"""
    def _gen(jobAppId):
        body_json = json.dumps({"resumes": "updated/updated/updated"})
        return {
            "body": body_json,
            "pathParameters": {"jobAppId": "%s" % (jobAppId)}
        }

    return _gen

def test_updateId_200(apigw_updateId_event,apigw_create_event):
    ret = update.handler(apigw_updateId_event(ids_created[0]), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200

def test_updateId_404(apigw_updateId_event):
    ret = update.handler(apigw_updateId_event("-1"), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 404


########################################################################
#                       DELETE BY ID TEST CASES                        #
########################################################################
@pytest.fixture()
def apigw_deleteId_event():
    """ Generates API GW Event"""
    def _gen(jobAppId):
        return {
            "body": '{}',
            "pathParameters": {"jobAppId": "%s" % (jobAppId)}
        }

    return _gen

def test_deleteId_200(apigw_deleteId_event):
    ret = delete.handler(apigw_deleteId_event(ids_created[0]), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200

def test_deleteId_404(apigw_deleteId_event):
    ret = delete.handler(apigw_deleteId_event("-1"), context)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 404

