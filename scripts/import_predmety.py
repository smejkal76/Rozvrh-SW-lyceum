
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.ucitel import Ucitel
from app.models.trida import Trida
from app.models.ucebna import Ucebna
from app.models.predmet import Predmet, ZamereniEnum
from app.models.vyucovaci_hodina import VyucovaciHodina  # pouze kvůli registraci FK v metadata

CSV_PATH = "data/predmet.csv"

REQUIRED = ["nazev", "zamereni", "puleny", "trida", "ucitel", "pocet_hodin"]

def _to_bool(v):
    s = str(v).strip().lower()
    return s in {"1.0", "1", "true", "t", "ano", "a", "y", "yes"}

def _parse_zamereni(v):
    # Pokud prázdné/NaN -> nepředáme hodnotu a necháme ORM default (vseobecny)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip().lower()
    if not s or s == "nan":
        return None
    if s in {"vseobecny", "humanitni", "prirodovedny"}:
        return ZamereniEnum[s]
    # Minimalisticky: pokud přijde něco jiného, považuj za chybu
    raise ValueError(f"Neplatné 'zamereni': {v!r} (povoleno: vseobecny/humanitni/prirodovedny)")

def main():
    df = pd.read_csv(CSV_PATH)

    # Kontrola hlavičky (minimalisticky)
    for c in REQUIRED:
        if c not in df.columns:
            raise ValueError(f"V CSV chybí povinný sloupec '{c}'.")

    session = SessionLocal()
    try:
        for i, r in df.iterrows():
            # Lookupy FK uvnitř no_autoflush, aby se neprováděl předčasný flush předchozích řádků
            with session.no_autoflush:
                id_tridy = session.execute(
                    select(Trida.id).where(Trida.nazev == str(r["trida"]).strip())
                ).scalar_one_or_none()
                if id_tridy is None:
                    raise ValueError(f"Řádek {i}: třída '{r['trida']}' nenalezena.")

                id_ucitele = session.execute(
                    select(Ucitel.id).where(Ucitel.prijmeni == str(r["ucitel"]).strip())
                ).scalar_one_or_none()
                if id_ucitele is None:
                    raise ValueError(f"Řádek {i}: učitel '{r['ucitel']}' nenalezen.")

                id_ucebny = None
                if "ucebna" in df.columns:
                    uv = r["ucebna"]
                    if pd.notna(uv) and str(uv).strip() != "":
                        id_ucebny = session.execute(
                            select(Ucebna.id).where(Ucebna.nazev == str(uv).strip())
                        ).scalar_one_or_none()
                        if id_ucebny is None:
                            raise ValueError(f"Řádek {i}: učebna '{uv}' nenalezena.")

            kwargs = dict(
                nazev=str(r["nazev"]).strip(),
                puleny=_to_bool(r["puleny"]),
                id_tridy=id_tridy,
                id_ucitele=id_ucitele,
                id_ucebny=id_ucebny,   # může být None
                id_hodiny=None,        # explicitně NULL dle zadání
                pocet_hodin=int(r["pocet_hodin"]),
            )
            zam = _parse_zamereni(r["zamereni"])
            if zam is not None:
                kwargs["zamereni"] = zam  # jinak se použije ORM default (vseobecny)

            p = Predmet(**kwargs)
            session.add(p)

        session.commit()
        print("Import 'predmet' (ORM) dokončen.")

        # --- Výpis tabulky predmet ---
        rows = session.execute(select(Predmet)).scalars().all()
        print("Obsah tabulky 'predmet':")
        for r in rows:
            print(f"{r.id}: {r.nazev}, zamereni={r.zamereni.name}, "
                  f"puleny={r.puleny}, trida_id={r.id_tridy}, "
                  f"ucitel_id={r.id_ucitele}, ucebna_id={r.id_ucebny}, "
                  f"pocet_hodin={r.pocet_hodin}, id_hodiny={r.id_hodiny}")

    finally:
        session.close()

if __name__ == "__main__":
    main()
