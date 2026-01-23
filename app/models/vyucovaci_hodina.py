from sqlalchemy import Column, Integer, Enum, String
from app.database import Base
import enum

class DenEnum(enum.Enum):
    Po = "Po"
    Ut = "Ut"
    St = "St"
    Ct = "Ct"
    Pa = "Pa"

class VyucovaciHodina(Base):
    __tablename__ = "vyucovaci_hodina"
    id = Column(Integer, primary_key=True)
    nazev = Column(String, nullable=False)
    den = Column(Enum(DenEnum), nullable=False)
    hodina_od = Column(Integer, nullable=False)
