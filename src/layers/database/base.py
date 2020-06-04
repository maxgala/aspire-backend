from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#rds settings
rds_host  = "aspire-db.cl3m8kiucudq.ca-central-1.rds.amazonaws.com"
rds_port = "5432"
name = "master"
password = "password"
db_name = "main_db"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(name, password, rds_host, rds_port, db_name))
Session = sessionmaker(bind=engine)

Base = declarative_base()
