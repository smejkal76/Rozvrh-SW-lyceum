from sqlalchemy import Column, Integer, ForeignKey, Enum, UniqueConstraint, String
from app.database import Base
import enum

class DenEnum(enum.Enum):
    Po = "Po"
    Ut = "Ut"
    St = "St"
    Ct = "Ct"
    Pa = "Pa"

class CasoveOmezeniUcitele(Base):
    __tablename__ = "casove_omezeni_ucitele"
    id = Column(Integer, primary_key=True)
    id_ucitele = Column(Integer, ForeignKey("ucitel.id"), nullable=False)
    den = Column(Enum(DenEnum), nullable=False)
    hodina_od = Column(Integer, nullable=False)
    delka = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("den", "hodina_od", "id_ucitele"),
    )

class CasoveOmezeniUcebny(Base):
    __tablename__ = "casove_omezeni_ucebny"
    id = Column(Integer, primary_key=True)
    id_ucebny = Column(Integer, ForeignKey("ucebna.id"), nullable=False)
    den = Column(Enum(DenEnum), nullable=False)
    hodina_od = Column(Integer, nullable=False)
    delka = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("den", "hodina_od", "id_ucebny"),
    )

class CasoveOmezeniRozvrhu(Base):
    __tablename__ = "casove_omezeni_rozvrhu"
    id = Column(Integer, primary_key=True)
    nazev = Column(String, nullable=False)
    den = Column(Enum(DenEnum), nullable=False)
    hodina_od = Column(Integer, nullable=False)
    delka = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("den", "hodina_od"),
    )
