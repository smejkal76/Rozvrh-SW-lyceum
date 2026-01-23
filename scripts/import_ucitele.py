import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.ucitel import Ucitel

CSV_PATH = "data/ucitel.csv"
df = pd.read_csv(CSV_PATH)

# očista dat
df["prijmeni"] = df["prijmeni"].astype(str).str.strip()
df = df.drop_duplicates(subset=["prijmeni"])

session = SessionLocal()
try:
    for prijmeni in df["prijmeni"]:
        exists = session.execute(
            select(Ucitel.id).where(Ucitel.prijmeni == prijmeni)
        ).scalar_one_or_none()
        if not exists:
            session.add(Ucitel(prijmeni=prijmeni))
    session.commit()

    # Výpis obsahu tabulky ucitel
    ucitele = session.execute(select(Ucitel)).scalars().all()
    print("Obsah tabulky UCITEL:")
    for u in ucitele:
        print(f"{u.id}: {u.prijmeni}")

finally:
    session.close()
