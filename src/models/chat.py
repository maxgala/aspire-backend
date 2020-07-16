import enum
from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import Mutable

from base import Base

class MenteeList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()
    def pop(self, index=0):
        value = list.pop(self, index)
        self.changed()
        return value

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MenteeList):
            if isinstance(value, list):
                return MenteeList(value)
            return Mutable.coerce(key, value)
        else:
            return value
        
class ChatType(enum.Enum):
    ONE_ON_ONE = 1
    ONE_ON_FOUR = 2

class ChatStatus(enum.Enum):
    PENDING = 1 # needs approval? not available for reservation yet
    ACTIVE = 2 # can only reserve a chat which is active
    RESERVED = 3 # once booked
    DONE = 4 # ????
    CANCELED = 5 # only through the editchat


credit_mapping = {ChatType.ONE_ON_ONE: 5, ChatType.ONE_ON_FOUR: 3}

class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(Integer(), primary_key=True)
    chat_type = Column(Enum(ChatType), nullable=False)
    description = Column(String(255))
    
    credits = Column(Integer(), nullable=False)
    
    date = Column(DateTime())
    # date and time of the actual chat 
    # YYYY-MM-DD HH:MM:SS
    
    chat_status = Column(Enum(ChatStatus), nullable=False)
    aspiring_professionals = Column(MenteeList.as_mutable(ARRAY(String(100))))
    #Column(ARRAY(String(100), dimensions=1))
    senior_executive = Column(String(100), nullable=False)
    
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    
    tags = Column(ARRAY(String(100), dimensions=1))
