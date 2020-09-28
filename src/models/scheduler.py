import enum
from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, BigInteger, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from base import Base, MutableList

class ChatType(enum.Enum):
    ONE_ON_ONE = 1
    ONE_ON_FOUR = 2
    MOCK_INTERVIEW = 3
    
class ChatStatus(enum.Enum):
    PENDING = 1 # needs approval? not available for reservation yet
    ACTIVE = 2 # can only reserve a chat which is active
    RESERVED = 3 # once booked
    DONE = 4 # ????
    CANCELED = 5 # only through the editchat

credit_mapping = {ChatType.ONE_ON_ONE: 5, ChatType.ONE_ON_FOUR: 3, \
                  ChatType.MOCK_INTERVIEW: 5}

mandatory_date = [ChatType.ONE_ON_FOUR, ChatType.MOCK_INTERVIEW]

class Scheduler(Base):
    __tablename__ = 'scheduler'

    chat_id = Column(Integer(), primary_key=True)
    chat_type = Column(Enum(ChatType), nullable=False)
    email = Column(String(255))
    
    end_date = Column(BigInteger())
    
    chat_status = Column(Enum(ChatStatus), nullable=False)
    fixed_date = Column(Boolean(), nullable = False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
