import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_url = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}"
# db_url = "postgresql+psycopg2://uzt_parser:darbO19@localhost/uzt_parser"

engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)


def create_db():
    Base.metadata.create_all(engine)
