import enum
from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, DateTime, Enum, Numeric

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
    posted_by = Column(String(100), nullable=False)
    contact_email = Column(String(255), nullable = False)
    job_status = Column(Enum(JobStatus), nullable=False)
    job_tags = Column(Enum(JobTags), nullable=False)
    salary = Column(Numeric(precision=2))
    deadline = Column(DateTime(), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    job_applications = relationship("JobApplication")