
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.ucebna import Ucebna
from app.models.omezeni import CasoveOmezeniUcebny  # mapování dle omezeni.py

CSV_PATH = "data/omezeni_ucebny.csv"

# Povinné sloupce v CSV
REQUIRED = ["ucebna", "den", "hodina_od", "delka"]

# Nastav na True, pokud chceš při chybě jen varovat a pokračovat (jinak selže řádek = vyvolá výjimku)
SKIP_ERRORS = False

# Pokud narazíme na duplicitní záznam podle (id_ucebny, den, hodina_od), můžeme místo selhání aktualizovat délku
UPSERT_ON_CONFLICT = True

DNY_POVOLENE = {"po": "Po", "út": "Ut", "ut": "Ut", "st": "St", "čt": "Ct", "ct": "Ct", "pa": "Pa", "pá": "Pa"}

def normalize_den(value: str) -> str:
    s = str(value).strip()
    if not s:
        return ""
    low = s.lower()
    # Odebrání teček, mezer apod.
    low = low.replace(".", "").replace(" ", "")
    # mapování variant s/bez diakritiky
    return DNY_POVOLENE.get(low, s)

def to_int_required(value, row_idx: int, col: str) -> int:
    s = str(value).strip()
    if not s or s.lower() == "nan":
        raise ValueError(f"Řádek {row_idx}: '{col}' je povinné a chybí.")
    try:
        return int(float(s))  # zvládne i '3.0'
    except ValueError:
        raise ValueError(f"Řádek {row_idx}: '{col}' musí být celé číslo, dostal jsem '{value}'.")

def lookup_ucebna_id(session, oznaceni: str, row_idx: int) -> int:
    v = str(oznaceni).strip()
    if not v or v.lower() == "nan":
        raise ValueError(f"Řádek {row_idx}: 'ucebna' je povinná a chybí.")
    _id = session.execute(select(Ucebna.id).where(Ucebna.nazev == v)).scalar_one_or_none()
    if _id is None:
        raise ValueError(f"Řádek {row_idx}: Učebna '{v}' nebyla nalezena v DB (pole 'oznaceni').")
    return _id

def main() -> None:
    df = pd.read_csv(CSV_PATH)

    # 1) Kontrola sloupců
    for col in REQUIRED:
        if col not in df.columns:
            raise ValueError(f"CSV musí obsahovat povinný sloupec '{col}'.")

    # 2) Očista textů
    df["ucebna"] = df["ucebna"].astype(str).str.strip()
    df["den"] = df["den"].astype(str).str.strip().apply(normalize_den)

    session = SessionLocal()
    inserted = 0
    updated = 0
    skipped = 0
    try:
        for idx, row in df.iterrows():
            try:
                # validace / převody
                id_ucebny = lookup_ucebna_id(session, row["ucebna"], idx)

                den = row["den"]
                if den not in {"Po", "Ut", "St", "Ct", "Pa"}:
                    raise ValueError(f"Řádek {idx}: 'den' musí být jeden z Po/Ut/St/Ct/Pa, dostal jsem '{row['den']}'.")

                hodina_od = to_int_required(row["hodina_od"], idx, "hodina_od")
                if not (1 <= hodina_od <= 7):
                    raise ValueError(f"Řádek {idx}: 'hodina_od' musí být v intervalu 1..7.")

                delka = to_int_required(row["delka"], idx, "delka")
                if delka <= 0:
                    raise ValueError(f"Řádek {idx}: 'delka' musí být kladná.")

                # pokus o vložení
                obj = CasoveOmezeniUcebny(
                    id_ucebny=id_ucebny,
                    den=den,
                    hodina_od=hodina_od,
                    delka=delka,
                )
                session.add(obj)
                try:
                    session.flush()  # pokus o INSERT bez commit
                    inserted += 1
                except IntegrityError:
                    session.rollback()
                    if UPSERT_ON_CONFLICT:
                        # najdi existující záznam a aktualizuj
                        existing = session.execute(
                            select(CasoveOmezeniUcebny).where(
                                (CasoveOmezeniUcebny.id_ucebny == id_ucebny) &
                                (CasoveOmezeniUcebny.den == den) &
                                (CasoveOmezeniUcebny.hodina_od == hodina_od)
                            )
                        ).scalar_one_or_none()
                        if existing:
                            existing.delka = delka
                            session.add(existing)
                            session.flush()
                            updated += 1
                        else:
                            raise
                    else:
                        raise

            except Exception as e:
                if SKIP_ERRORS:
                    skipped += 1
                    print(f"Řádek {idx}: přeskočeno ({e})")
                    session.rollback()
                    continue
                else:
                    session.rollback()
                    raise

        session.commit()
        print(f"Hotovo. Vloženo: {inserted}, aktualizováno: {updated}, přeskočeno: {skipped}")

        # Volitelně: výpis výsledků
        rows = session.execute(select(CasoveOmezeniUcebny)).scalars().all()
        print("Obsah tabulky casove_omezeni_ucebny:")
        for r in rows:
            print(f"{r.id}: ucebna_id={r.id_ucebny} | den={r.den} | hodina_od={r.hodina_od} | delka={r.delka}")

    finally:
        session.close()

if __name__ == "__main__":
    main()
