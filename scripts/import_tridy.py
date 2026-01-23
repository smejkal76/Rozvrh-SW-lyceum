# scripts/import_tridy.py
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.trida import Trida

CSV_PATH = "data/trida.csv"

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
                select(Trida.id).where(Trida.nazev == nazev)
            ).scalar_one_or_none()
            if not exists:
                session.add(Trida(nazev=nazev))
        session.commit()

        # 3) Výpis obsahu tabulky
        print("Obsah tabulky trida:")
        tridy = session.execute(select(Trida)).scalars().all()
        for t in tridy:
            print(f"{t.id}: {t.nazev}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
