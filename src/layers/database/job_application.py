import enum
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.orm import relationship

from base import Base

class JobApplicationStatus(enum.Enum):
    SUBMIT = 1
    REVIEW = 2
    OFFER_EXTEND = 3
    OFFER_ACCEPT = 4
    OFFER_REJECT = 5


class JobApplication(Base):
    __tablename__ = 'job_applications'

    job_application_id = Column(Integer(), primary_key=True)
    job_id = Column(Integer(), ForeignKey('jobs.job_id'), nullable=False)
    applicant_id = Column(Integer(), ForeignKey('users.user_id'), nullable=False)
    job_application_status = Column(Enum(JobApplicationStatus), nullable=False)
    documents = Column(String(255), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
