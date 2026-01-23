import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.omezeni import CasoveOmezeniRozvrhu, DenEnum

CSV_PATH = "data/omezeni_rozvrhu.csv"
REQUIRED = ["nazev", "den", "hodina_od", "delka"]

# Povolené hodnoty pro dny s normalizací variant s/bez diakritiky
_MAP_DEN = {
    "po": "Po",
    "út": "Ut", "ut": "Ut",
    "st": "St",
    "čt": "Ct", "ct": "Ct",
    "pa": "Pa", "pá": "Pa",
}

def _parse_den(v):
    s = str(v).strip().lower().replace(".", "").replace(" ", "")
    if s not in _MAP_DEN:
        raise ValueError(f"Neplatný den: {v!r}. Povoleno: {list(_MAP_DEN.keys())}.")
    return DenEnum[_MAP_DEN[s]]

def _to_int(v, name):
    try:
        return int(float(str(v).strip()))
    except Exception:
        raise ValueError(f"Sloupec '{name}' musí být celé číslo, dostal jsem {v!r}.")

def main():
    df = pd.read_csv(CSV_PATH)

    for c in REQUIRED:
        if c not in df.columns:
            raise ValueError(f"V CSV chybí povinný sloupec '{c}'.")

    session = SessionLocal()
    try:
        for i, r in df.iterrows():
            obj = CasoveOmezeniRozvrhu(
                nazev=str(r["nazev"]).strip(),
                den=_parse_den(r["den"]),
                hodina_od=_to_int(r["hodina_od"], "hodina_od"),
                delka=_to_int(r["delka"], "delka"),
            )
            session.add(obj)

        session.commit()
        print("Import 'casove_omezeni_rozvrhu' dokončen.\n")

        # Výpis tabulky na konzoli
        rows = session.execute(select(CasoveOmezeniRozvrhu)).scalars().all()
        print("Obsah tabulky 'casove_omezeni_rozvrhu':")
        for r in rows:
            print(f"{r.id}: {r.nazev} | den={r.den.name} | hodina_od={r.hodina_od} | delka={r.delka}")

    finally:
        session.close()

if __name__ == "__main__":
    main()
