import enum
from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Enum, ARRAY

from base import Base

class ChatType(enum.Enum):
    ONE_ON_ONE = 1
    ONE_ON_FOUR = 2
    MOCK_INTERVIEW = 3


class ChatStatus(enum.Enum):
    PENDING = 1
    ACTIVE = 2
    RESERVED = 3
    DONE = 4
    CANCELED = 5


class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(Integer(), primary_key=True)
    date = Column(DateTime(), nullable=False)
    # timestamp in long since 1970
    # return object in response payload
    
    chat_type = Column(Enum(ChatType), nullable=False)
    description = Column(String(255))
    credits = Column(Integer(), nullable=False)
    chat_status = Column(Enum(ChatStatus), nullable=False)
    aspiring_professionals = Column(ARRAY(String(100), dimensions=1))
    senior_executive = Column(String(100), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
