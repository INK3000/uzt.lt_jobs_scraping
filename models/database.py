from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = "uzt_job_db.sqlite"
engine = create_engine("postgresql+psycopg2://uzt_parser:darbO19@localhost/uzt_parser")
Base = declarative_base()
Session = sessionmaker(bind=engine)


def create_db():
    Base.metadata.create_all(engine)
