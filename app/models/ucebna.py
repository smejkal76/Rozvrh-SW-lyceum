from sqlalchemy import Column, Integer, String
from app.database import Base

class Ucebna(Base):
    __tablename__ = "ucebna"
    id = Column(Integer, primary_key=True)
    nazev = Column(String, unique=True, nullable=False)
