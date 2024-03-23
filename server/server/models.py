from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import Mapped

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
