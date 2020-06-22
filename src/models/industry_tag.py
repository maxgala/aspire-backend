from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String

from base import Base


class IndustryTag(Base):
    __tablename__ = 'industry_tags'

    tag = Column(String(100), primary_key=True)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)