"""
    Krok 1. Test kontrolních součtů po importu dat
"""

from app.database import SessionLocal
from app.models.predmet import Predmet
from app.models.trida import Trida
from app.models.ucitel import Ucitel
from app.models.ucebna import Ucebna
from app.models.omezeni import CasoveOmezeniUcebny
from app.models.omezeni import CasoveOmezeniUcitele
from app.models.omezeni import CasoveOmezeniRozvrhu


if __name__ == "__main__":
    session = SessionLocal()
    print("[K1] Připojeno k DB.")
    print("[K1] Počty záznamů:")
    for model in [Predmet, Trida, Ucitel, Ucebna, CasoveOmezeniUcitele, CasoveOmezeniUcebny, CasoveOmezeniRozvrhu]:
        cnt = session.query(model).count()
        print(f"   - {model.__name__}: {cnt}")