from models.database import Base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (UniqueConstraint('user_tg_id', sqlite_on_conflict='IGNORE'),)

    id: Column = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(String)
    subscribes = Column(String)

    def __repr__(self):
        return f'id:{self.id}, user_tg_id: {self.user_tg_id}, category:{self.category}'

