import enum
import decimal
import os
from dotenv import load_dotenv
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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
            if len(val) == 0:
                val = []
            elif isinstance(val[0], enum.Enum):
                val = [v.name for v in val]
        d[key] = val
    return d

load_dotenv()
rdsHost= os.getenv('RDS_HOST')
rdsPort= os.getenv('RDS_PORT')
rdsUsername= os.getenv('RDS_USERNAME')
rdsPassword= os.getenv('RDS_PASSWORD')
rdsDbName= os.getenv('RDS_DB_NAME')

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(rdsUsername, rdsPassword, rdsHost, rdsPort, rdsDbName))
Session = sessionmaker(bind=engine)

Base = declarative_base()
