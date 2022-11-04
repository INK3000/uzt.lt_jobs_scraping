from models.database import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)
    category = Column(Integer, ForeignKey('categories.id'))
    company = Column(String)
    date_from = Column(String)
    date_to = Column(String)
    name = Column(String)
    place = Column(String)
    url = Column(String)

    def __repr__(self):
        return f'Company: {self.company} Job title: {self.name} Place: {self.place}, url: {self.url}'
