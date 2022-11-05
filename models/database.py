from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


DATABASE_NAME = 'uzt_job_db.sqlite'
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Base = declarative_base()
Session = sessionmaker(bind=engine)


def create_db():
    Base.metadata.create_all(engine)


def is_exist_db(database_name):
    return os.path.exists(database_name)



