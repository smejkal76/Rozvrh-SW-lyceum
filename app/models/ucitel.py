from sqlalchemy import Column, Integer, String
from app.database import Base

class Ucitel(Base):
    __tablename__ = "ucitel"
    id = Column(Integer, primary_key=True)
    prijmeni = Column(String, unique=True, nullable=False)
