from models.database import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    event_target = Column(String)

    def __repr__(self):
        return f'id: {self.id} / category: {self.name} / event_target: {self.event_target}'
