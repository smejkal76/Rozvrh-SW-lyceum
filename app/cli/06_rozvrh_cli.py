"""
    Krok 5. Seřazení naplánovaných úloh podle kritérií jako obtížnost, blokace či délka.
"""

from app.database import SessionLocal
from app.models.omezeni import CasoveOmezeniUcebny, CasoveOmezeniUcitele, DenEnum
from app.generator.calendars import Calendars, DAYS
from app.generator.tasks import build_tasks, group_halves, Uloha
from app.generator.sort_tasks import sort_items


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

    # Spojení půlených hodin
    plan_items = group_halves(ulohy, strict_pairs=False)
    print(f"[K4] Plánovacích položek: {len(plan_items)} | svazků: {sum(hasattr(x,'parts') for x in plan_items)}")

    plan_items = sort_items(cal, plan_items)
    print("[K5] Položky seřazeny:")
    for it in plan_items:
        print("   ", it.nazev, "   L=", it.pocet_hodin, ("   SPOJENÉ" if hasattr(it,'parts') else "   učebna:" + str(it.id_ucebny)))



