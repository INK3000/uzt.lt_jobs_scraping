from models.database import Base
from sqlalchemy import Column, Integer, String, UniqueConstraint


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("user_tg_id", sqlite_on_conflict="IGNORE"),)

    id: Column = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer)
    subscribes = Column(String)

    def __repr__(self):
        return (
            f"id:{self.id}, user_tg_id: {self.user_tg_id}, category:{self.subscribes}"
        )
