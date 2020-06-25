import enum
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
        elif isinstance(val, list):
            if isinstance(val[0], enum.Enum):
                val = [v.name for v in val]
        d[key] = val
    return d


#rds settings
rds_host  = "aspire-db.cl3m8kiucudq.ca-central-1.rds.amazonaws.com"
rds_port = "5432"
name = "master"
password = "password"
db_name = "main_db"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(name, password, rds_host, rds_port, db_name))
Session = sessionmaker(bind=engine)

Base = declarative_base()
