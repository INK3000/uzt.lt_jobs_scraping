from models.database import Base

from sqlalchemy import Column
from sqlalchemy import UniqueConstraint
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey


class Job(Base):
    __tablename__ = 'jobs'
    __table_args__ = (UniqueConstraint('category', 'url', sqlite_on_conflict='IGNORE'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_upd = Column(String)
    category = Column(Integer, ForeignKey('categories.id'))
    company = Column(String)
    date_from = Column(String)
    date_to = Column(String)
    name = Column(String)
    place = Column(String)
    url = Column(String)

    def __repr__(self):
        return f'Company: {self.company} Job title: {self.name} Place: {self.place}, url: {self.url}'
