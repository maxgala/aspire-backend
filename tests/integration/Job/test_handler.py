import sys
import os
import json
import pytest

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/Job" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/lambda/JobApplications" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
from CreateJob import lambda_function as create
from DeleteJobById import lambda_function as delete
from GetAllJobs import lambda_function as get_all
from GetJobById import lambda_function as get
from EditJobById import lambda_function as edit
from CloseJobById import lambda_function as close
from JobContactById import lambda_function as contact

from CreateJobApplication import lambda_function as createApp
from DeleteJobApplicationById import lambda_function as deleteApp

context = ""
ids_created = []
########################################################################
#                          CREATE TEST CASES                           #
########################################################################

def test_create_201():
    event = {}
    request = {
            "title":"Software Developer",
            "company":"My-Company",
            "region":"ON",
            "city":"Waterloo",
            "country":"Canada",
            "job_type": "BOARD_POSITION",
            "description":"XYZ",
            "requirements":"XYZ",
            "job_tags":["SOFTWARE","FINANCE"],
            "salary":40,
            "deadline":1593718782,
            "posted_by": "test@email.xyz",
            "poster_family_name": "Suleman",
            "poster_given_name": "S"
        }
    event["body"] = json.dumps(request)
    actual = {}
    actual = create.handler(event, context)
    assert actual["statusCode"] == 201
    actual_body = json.loads(actual["body"])
    ids_created.append(actual_body["job"]["job_id"])
    print(ids_created)
    

'''
    ret = create.handler(apigw_create_event("tag2"), "")
    assert ret["statusCode"] == 201

    ret = create.handler(apigw_create_event("tag3"), "")
    assert ret["statusCode"] == 201

    ret = create.handler(apigw_create_event("other tag"), "")
    assert ret["statusCode"] == 201
'''


########################################################################
#                          GET ALL TEST CASES                          #
########################################################################
@pytest.fixture()
def apigw_getAll_event():
    """ Generates API GW Event"""
    def _gen():
        return {
            "body": None,
            "queryStringParameters": None
        }

    return _gen

@pytest.fixture()
def apigw_getAllUserId_event():
    """ Generates API GW Event"""
    def _gen(user_id):
        return {
            "body": None,
            "queryStringParameters": {"user_id": "%s" % (user_id)}
        }

    return _gen

@pytest.fixture()
def apigw_getAllStatus_event():
    """ Generates API GW Event"""
    def _gen(status):
        return {
            "body": None,
            "queryStringParameters": {"status": "%s" % (status)}
        }

    return _gen

def test_getAll_200(apigw_getAll_event):
    ret = get_all.handler(apigw_getAll_event(), "")
    data = json.loads(ret["body"])
    actual_job_ids = [record["job_id"] for record in data['jobs']]

    assert ret["statusCode"] == 200
    for jobid in ids_created:
        assert jobid in actual_job_ids

def test_getAllUserId_200(apigw_getAllUserId_event):
    ret = get_all.handler(apigw_getAllUserId_event("test@email.xyz"), "")
    data = json.loads(ret["body"])
    actual_job_ids = [record["job_id"] for record in data['jobs']]

    assert ret["statusCode"] == 200
    assert ids_created[0] in actual_job_ids

def test_getAllOpen_200(apigw_getAllStatus_event):
    ret = get_all.handler(apigw_getAllStatus_event("open"), "")
    data = json.loads(ret["body"])
    actual_job_ids = [record["job_id"] for record in data['jobs']]

    assert ret["statusCode"] == 200
    assert ids_created[0] in actual_job_ids



########################################################################
#                         GET BY ID TEST CASES                         #
########################################################################
@pytest.fixture()
def apigw_get_event():
    """ Generates API GW Event"""
    def _gen(job_id):
        return {
            "body": '{}',
            "pathParameters": {"jobId": "%s" % (job_id)}
        }

    return _gen

def test_get_200(apigw_get_event):
    for jobid in ids_created:
        ret = get.handler(apigw_get_event(jobid), "")
        data = json.loads(ret["body"])

        assert ret["statusCode"] == 200
        assert jobid == data["job_id"]


def test_get_404(apigw_get_event):
    ret = get.handler(apigw_get_event(-1), "")

    assert ret["statusCode"] == 404

########################################################################
#                         CLOSE BY ID TEST CASES                         #
########################################################################
@pytest.fixture()
def apigw_close_event():
    """ Generates API GW Event"""
    def _gen(job_id):
        return {
            "body": '{}',
            "pathParameters": {"jobId": "%s" % (job_id)}
        }

    return _gen

def test_close_200(apigw_get_event, apigw_close_event):
    ret = close.handler(apigw_close_event(ids_created[0]), "")
    get_ret = get.handler(apigw_get_event(ids_created[0]), "")
    data = json.loads(get_ret["body"])

    assert ret["statusCode"] == 200
    assert "CLOSED" == data["job_status"]


def test_close_404(apigw_close_event):
    ret = close.handler(apigw_close_event(-1), "")

    assert ret["statusCode"] == 404

########################################################################
#                         EDIT BY ID TEST CASES                         #
########################################################################
@pytest.fixture()
def apigw_edit_event():
    """ Generates API GW Event"""
    def _gen(job_id):
        return {
            "body": '{"title":"updated-title"}',
            "pathParameters": {"jobId": "%s" % (job_id)}
        }

    return _gen

def test_edit_200(apigw_get_event, apigw_edit_event):
    ret = edit.handler(apigw_edit_event(ids_created[0]), "")
    get_ret = get.handler(apigw_get_event(ids_created[0]), "")
    data = json.loads(get_ret["body"])

    assert ret["statusCode"] == 200
    assert data["title"] == "updated-title"


def test_edit_404(apigw_edit_event):
    ret = edit.handler(apigw_edit_event(-1), "")
    assert ret["statusCode"] == 404



########################################################################
#                       DELETE BY ID TEST CASES                        #
########################################################################
@pytest.fixture()
def apigw_delete_event():
    """ Generates API GW Event"""
    def _gen(job_id):
        return {
            "body": '{}',
            "pathParameters": {"jobId": "%s" % (job_id)}
        }

    return _gen
'''
def test_delete_409(apigw_delete_event):
    event = {}
    request = {
        "job_id": "%s" % (ids_created[0]),
        "job_application_status": "OFFER_REJECT",
        "applicant_id": "test@email.com",
        "resumes": "resumes/path-goes-here",
        "cover_letters": "cover_letters/path-goes-here"
    }
    event["body"] = json.dumps(request)
    actual = {}
    actual = createApp.handler(event, context)
    assert actual["statusCode"] == 201
    ret = delete.handler(apigw_delete_event(ids_created[0]), "")
    assert ret["statusCode"] == 409
    del_app = deleteApp.handler(apigw_delete_event(ids_created[0]), "")
'''
def test_delete_200(apigw_delete_event):
    for jobid in ids_created:
        ret = delete.handler(apigw_delete_event(jobid), "")
        assert ret["statusCode"] == 200

def test_delete_404(apigw_delete_event):
    for jobid in ids_created:
        ret = delete.handler(apigw_delete_event(jobid), "")
        assert ret["statusCode"] == 404

    ret = delete.handler(apigw_delete_event(-1), "")
    assert ret["statusCode"] == 404

