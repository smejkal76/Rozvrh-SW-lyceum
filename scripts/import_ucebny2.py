# scripts/import_ucebny.py
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.ucebna import Ucebna

CSV_PATH = "data/ucebna.csv"

# 1) Načtení CSV
df = pd.read_csv(CSV_PATH) # df jako datafile

# 2) Uložení do DB (přeskočí již existující)
session = SessionLocal()
for nazev in df["nazev"]:
    session.add(Ucebna(nazev=nazev))
session.commit()

# 3) Výpis obsahu tabulky
print("Obsah tabulky UCEBNA:")
ucebny = session.execute(select(Ucebna)).scalars().all()
for u in ucebny:
    print(f"{u.id}: {u.nazev}")

session.close()
