import enum
from datetime import datetime
from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.types import String, Integer, Enum, DateTime

from base import Base


class ConnectStatus(enum.Enum):
    PENDING = 1
    ACCEPTED = 2
    CANCELLED = 3
    DECLINED = 4


class ConnectSE(Base):
    __tablename__ = 'senior-exec-connect'

    connect_id = Column(Integer(), primary_key=True)
    requestor = Column(String(100), nullable=False)
    requestee = Column(String(100), nullable=False)

    connect_status = Column(Enum(ConnectStatus), nullable=False)

    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
