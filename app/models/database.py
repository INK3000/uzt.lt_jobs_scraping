from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://uzt_parser:darbO19@localhost/uzt_parser")
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)


def create_db():
    Base.metadata.create_all(engine)