import json
import logging

from connection import Connection, ConnectionStatus
from chat import Chat, ChatType, ChatStatus
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from industry_tag import IndustryTag
from connection import ConnectionStatus, Connection
from base import Session, engine, Base

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    #  generate database tables
    Base.metadata.create_all(engine)

    return {
        "statusCode": 201
    }
