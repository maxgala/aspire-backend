import enum
from datetime import datetime
from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.orm import relationship

from base import Base

class ChatType(enum.Enum):
    ONE_ON_ONE = 1
    ONE_ON_FOUR = 2


class ChatStatus(enum.Enum):
    PENDING = 1
    DONE = 2
    CANCELED = 3


# FOR REFERENCE
# chats_aspiring_professionals_association = Table('chats_aspiring_professionals', Base.metadata,
#     Column('chat_id', Integer, ForeignKey('chats.chat_id')),
#     Column('user_id', Integer, ForeignKey('users.user_id'))
# )

# chats_senior_executives_association = Table('chats_senior_executives', Base.metadata,
#     Column('chat_id', Integer, ForeignKey('chats.chat_id')),
#     Column('user_id', Integer, ForeignKey('users.user_id'))
# )


class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(Integer(), primary_key=True)
    date = Column(DateTime(), nullable=False)
    chat_type = Column(Enum(ChatType), nullable=False)
    description = Column(String(255))
    credits = Column(Integer(), nullable=False)
    chat_status = Column(Enum(ChatStatus), nullable=False)
    # aspiring_professionals = relationship("User", secondary=chats_aspiring_professionals_association)
    # senior_executives = relationship("User", secondary=chats_senior_executives_association)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
