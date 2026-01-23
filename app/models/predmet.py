from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from app.database import Base
import enum

class ZamereniEnum(enum.Enum):
    vseobecny = "vseobecny"
    humanitni = "humanitni"
    prirodovedny = "prirodovedny"

"""
Logika tabulky PREDMET není daný předmět pro danou třídu jedenkrát, ale jedná se o seznam hodin, 
které je potřeba umístit do rozvrhu. 
V tabulce tedy neexistuje žádná unikátní kombinace sloupců. Jediný unique je ID.
"""
class Predmet(Base):
    __tablename__ = "predmet"

    id = Column(Integer, primary_key=True)
    nazev = Column(String, nullable=False)
    zamereni = Column(Enum(ZamereniEnum, name="typ_zamereni"),
                      nullable=False, default=ZamereniEnum.vseobecny)
    puleny = Column(Boolean, nullable=False, default=False)
    pocet_hodin = Column(Integer, nullable=False)

    id_tridy   = Column(Integer, ForeignKey("trida.id"),   nullable=False)
    id_ucitele = Column(Integer, ForeignKey("ucitel.id"),  nullable=False)
    id_ucebny  = Column(Integer, ForeignKey("ucebna.id"),  nullable=True)
    id_hodiny  = Column(Integer, ForeignKey("vyucovaci_hodina.id"),  nullable=True)

