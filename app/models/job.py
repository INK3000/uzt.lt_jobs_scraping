from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from models.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("category", "url"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_upd = Column(String)
    category = Column(Integer, ForeignKey("categories.id"))
    company = Column(String)
    date_from = Column(String)
    date_to = Column(String)
    name = Column(String)
    place = Column(String)
    url = Column(String)

    def __repr__(self):
        return f"Company: {self.company} Job title: {self.name} Place: {self.place}, url: {self.url}, id: {self.id}"

    def __hash__(self):
        return hash((self.url, self.category))

    def __eq__(self, other):
        return self.url == other.url and self.category == other.category
