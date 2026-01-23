# scripts/import_ucebny.py
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.ucebna import Ucebna

CSV_PATH = "data/ucebna.csv"

def main() -> None:
    # 1) Načtení a očista CSV
    df = pd.read_csv(CSV_PATH)
    if "nazev" not in df.columns:
        raise ValueError("CSV musí obsahovat sloupec 'nazev'.")

    df["nazev"] = df["nazev"].astype(str).str.strip()
    df = df[df["nazev"] != ""]
    df = df.drop_duplicates(subset=["nazev"])

    # 2) Uložení do DB (přeskočí již existující)
    session = SessionLocal()
    try:
        for nazev in df["nazev"]:
            exists = session.execute(
                select(Ucebna.id).where(Ucebna.nazev == nazev)
            ).scalar_one_or_none()
            if not exists:
                session.add(Ucebna(nazev=nazev))
        session.commit()

        # 3) Výpis obsahu tabulky
        print("Obsah tabulky UCEBNA:")
        ucebny = session.execute(select(Ucebna)).scalars().all()
        for u in ucebny:
            print(f"{u.id}: {u.nazev}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
