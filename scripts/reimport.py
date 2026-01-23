
"""
reimport.py
- Promaže DB tabulky (TRUNCATE ... RESTART IDENTITY CASCADE)
- Spustí všechny importní skripty v doporučeném pořadí
Použití:
    python reimport.py --dir scripts_or_project_root
Pokud --dir neuvedete, použije se aktuální pracovní adresář.
"""
import argparse
import sys
import runpy
from pathlib import Path
from typing import List

from sqlalchemy import text
from app.database import SessionLocal

# Pořadí TRUNCATE dle FK závislostí z DDL (hodiny -> omezení -> předměty -> varianta -> základní tabulky)
# (viz 20 SQL DDL.sql)
TRUNCATE_ORDER = [
    "vyucovaci_hodina",
    "casove_omezeni_ucitele",
    "casove_omezeni_ucebny",
    "casove_omezeni_rozvrhu",
    "predmet",
    "trida",
    "ucitel",
    "ucebna",
]

# Pořadí importů — nejdřív referencovaná data, pak od nich závislá
IMPORT_SCRIPTS = [
    "import_tridy.py",
    "import_ucitele.py",
    "import_ucebny.py",
    "import_predmety.py",
    "import_casove_omezeni_ucitele.py",
    "import_casove_omezeni_ucebny.py",
    "import_casove_omezeni_rozvrhu.py",
]

def reset_db() -> None:
    """TRUNCATE tabulek a reset ID sekvencí; CASCADE ošetří návaznosti, držíme i korektní pořadí."""
    stmt = f"TRUNCATE TABLE {', '.join(TRUNCATE_ORDER)} RESTART IDENTITY CASCADE;"
    with SessionLocal() as session:
        session.execute(text(stmt))
        session.commit()
    print("DB: TRUNCATE hotovo. ID sekvence resetovány.")

def run_scripts(base_dir: Path, scripts: List[str]) -> None:
    for name in scripts:
        path = (base_dir / name).resolve()
        if not path.exists():
            # zkus fallback: když je skript vedle reimport.py
            alt = Path.cwd() / name
            if alt.exists():
                path = alt.resolve()
            else:
                raise FileNotFoundError(f"Nenalezen importní skript: {name} (hledáno v {base_dir})")
        print(f"\n=== Spouštím {path.name} ===")
        # Spuštění jako by byl volán z příkazové řádky (__main__)
        runpy.run_path(str(path), run_name="__main__")
        print(f"=== Hotovo {path.name} ===")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Reimport dat podle DDL a import skriptů.")
    parser.add_argument("--dir", type=str, default=".", help="Kořenová složka s import skripty (default: aktuální).")
    args = parser.parse_args(argv)

    base_dir = Path(args.dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Složka '{base_dir}' neexistuje.")

    print("== KROK 1/2: Reset DB ==")
    reset_db()

    print("\n== KROK 2/2: Import dat ==")
    run_scripts(base_dir, IMPORT_SCRIPTS)

    print("\nVše dokončeno.")

if __name__ == "__main__":
    main()
