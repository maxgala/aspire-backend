import enum
from datetime import datetime
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, DateTime, Enum

from base import Base

class JobApplicationStatus(enum.Enum):
    SUBMIT = 1
    REVIEW = 2
    INVITE = 3
    OFFER_EXTEND = 4
    OFFER_ACCEPT = 5
    OFFER_REJECT = 6


class JobApplication(Base):
    __tablename__ = 'job_applications'

    job_application_id = Column(Integer(), primary_key=True)
    job_id = Column(Integer(), ForeignKey('jobs.job_id'), nullable=False)
    applicant_id = Column(String(100), nullable=False)
    job_application_status = Column(Enum(JobApplicationStatus), nullable=False)
    resumes = Column(String(255), nullable=False)
    cover_letters = Column(String(255), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    