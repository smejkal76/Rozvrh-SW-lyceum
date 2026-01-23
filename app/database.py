from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from os import getenv

# Přečte .env soubor a uloží hodnoty do environmentálních proměnných
load_dotenv()
# Získá hodnotu proměnné DATABASE_URL
DATABASE_URL = getenv("DATABASE_URL")

"""
    Vytvoří objekt engine, který:
        zná typ databáze a driver,
        umí otevírat připojení,
        spravuje connection pool,
        komunikuje s DB na nízké úrovni.
"""
engine = create_engine(DATABASE_URL)

"""
    Vytvoří továrnu na sessions. Pokaždé, když zavoláš SessionLocal(), dostaneš novou session navázanou na engine.

    Využito později při CRUD, např.:
        session = SessionLocal()
        session.add(Ucitel(prijmeni=prijmeni))
"""
SessionLocal = sessionmaker(bind=engine)

"""
    Vytvoří základní třídu pro ORM.
    
    Každý model pak dědí z Base:
        class Ucitel(Base):
"""
Base = declarative_base()
