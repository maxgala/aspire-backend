import enum
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Enum, Numeric
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects import postgresql
from base import Base

class JobType(enum.Enum):
    BOARD_POSITION = 1
    REGULAR_JOB = 2


class JobStatus(enum.Enum):
    OPEN = 1
    CLOSED = 2


class JobTags(enum.Enum):
    SOFTWARE = 1
    FINANCE = 2
    LAW = 3


class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(Integer(), primary_key=True)
    title = Column(String(255), nullable = False)
    company = Column(String(255))
    province = Column(String(255), nullable = False)
    city = Column(String(255), nullable = False)
    num_applicants = Column(Integer(), default=0)
    job_type = Column(Enum(JobType), nullable=False)
    description = Column(String(), nullable = False)
    requirements = Column(String(), nullable = False)
    posted_by = Column(Integer(), nullable=False)
    contact_email = Column(String(255), nullable = False)
    job_status = Column(Enum(JobStatus), nullable=False)
    job_tags = Column(Enum(JobTags), nullable=False)
    salary = Column(Numeric(precision=2))
    deadline = Column(DateTime(), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    job_applications = relationship("JobApplication")
