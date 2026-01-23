"""
    Krok 3. Přidáno načtení úloh pro rozvržení z tabulky PREDMET
"""

from app.database import SessionLocal
from app.models.omezeni import CasoveOmezeniUcebny, CasoveOmezeniUcitele
from app.generator.calendars import Calendars
from app.generator.tasks import build_tasks

def load_constraints(sess, calendars):
    # učitelé
    for o in sess.query(CasoveOmezeniUcitele).all():
        calendars.mark_teacher(o.id_ucitele, o.den, o.hodina_od, o.delka)
    # učebny
    for o in sess.query(CasoveOmezeniUcebny).all():
        calendars.mark_room(o.id_ucebny, o.den, o.hodina_od, o.delka)

if __name__ == "__main__":
    session = SessionLocal()

    cal = Calendars()
    load_constraints(session, cal)

    ulohy = build_tasks(session)
    print(f"[K3] Načteno úloh: {len(ulohy)}")
    print("[K3] Ukázka prvních 5:")
    for u in ulohy[:5]:
        print("   ", u)