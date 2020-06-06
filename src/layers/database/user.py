# FOR REFERENCE

import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.orm import relationship

from base import Base

class UserType(enum.Enum):
    ASPIRING_PROFESSIONAL = 1
    SENIOR_EXECUTIVE = 2
    ADMIN = 3


class MembershipType(enum.Enum):
    PREMIUM = 1
    FREE_TIER = 2


class IndustryTags(enum.Enum):
    COMPUTER_SOFTWARE = 1
    COMPUTER_HARDWARE = 2


class EducationLevel(enum.Enum):
    HIGHSCHOOL = 1
    DIPLOMA = 2
    BACHELORS = 3
    MASTERS = 4
    DOCTORATE = 5


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer(), primary_key=True)
    username = Column(String(25), nullable=False, unique=True)
    email_address = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    industry = Column(Enum(IndustryTags))
    position = Column(String(50), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    phone_number = Column(String(50))
    birth_year = Column(Integer(), nullable=False)
    company = Column(String(100))
    education_level = Column(Enum(EducationLevel), nullable=False)
    country = Column(String(50), nullable=False)
    province = Column(String(50), nullable=False)
    resume = Column(String(255))
    photo = Column(String(255))
    linkedin = Column(String(255))
    credits = Column(Integer(), nullable=False)
    membership_type = Column(Enum(MembershipType), nullable=False)
    password = Column(String(255), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    #jobs = relationship("Job")
