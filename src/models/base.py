import enum
import decimal
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.mutable import Mutable

class MutableList(Mutable, list):
    ''' Use case: when the col type is ARRAY
    and is expected to change.

    To create a new entry:
    l = [...]
    Table.Col = MutableList.coerce(Table.Col, l)

    To update an existing entry, treat it as a
    typical Pythonic list:
    Table.Col.append(val)
    '''
    @classmethod # call MutableList.coerce()
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value
        
    def append(self, value):
        list.append(self, value)
        self.changed()
    def pop(self, index=0):
        value = list.pop(self, index)
        self.changed()
        return value

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        key = column.name
        val = getattr(row, column.name)
        if isinstance(val, datetime):
            val = val.timestamp()
        elif isinstance(val, enum.Enum):
            val = val.name
        elif isinstance(val, decimal.Decimal):
            val = float(val)
        elif isinstance(val, list):
            if isinstance(val[0], enum.Enum):
                val = [v.name for v in val]
        d[key] = val
    return d

rdsHost= os.getenv('RDS_HOST')
rdsPort= os.getenv('RDS_PORT')
rdsUsername= os.getenv('RDS_USERNAME')
rdsPassword= os.getenv('RDS_PASSWORD')
rdsDbName= os.getenv('RDS_DB_NAME') 

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(rdsUsername, rdsPassword, rdsHost, rdsPort, rdsDbName))
Session = sessionmaker(bind=engine)

Base = declarative_base()
