from sqlalchemy import Column, Integer, String
from app.database import Base

class Trida(Base):
    __tablename__ = "trida"
    id = Column(Integer, primary_key=True)
    nazev = Column(String, unique=True, nullable=False)

    def __repr__(self):
        # Rozdíl mezi metodami __str__() a __repr__(): objekty se převádějí na řetězce – a to buď
        # pro uživatele, nebo pro vývojáře.
        return f"id={self.id}, nazev={self.nazev}"