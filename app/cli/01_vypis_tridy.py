"""
    Test mapování tabulky TRIDA
"""

from app.database import Base, SessionLocal
from app.models.trida import Trida

# Vytvoření session
session = SessionLocal()

# Načtení všech tříd z databáze a výpis
tridy = session.query(Trida).all()
for trida in tridy:
    print(trida)
session.close()
