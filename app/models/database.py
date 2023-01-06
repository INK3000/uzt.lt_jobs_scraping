from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

db_url = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}"
print(db_url)

engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)


def create_db():
    Base.metadata.create_all(engine)
