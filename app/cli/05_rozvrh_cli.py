"""
    Krok 4. Přidáno spojení půlených hodin do plan_items.
"""

from app.database import SessionLocal
from app.models.omezeni import CasoveOmezeniUcebny, CasoveOmezeniUcitele
from app.generator.calendars import Calendars
from app.generator.tasks import build_tasks, group_halves

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

    # Výpis párů i nepůlených hodin
    for i, it in enumerate(x for x in plan_items if hasattr(x,'parts')):
        print(i + 1, f"   [SLOUCENA] key={it.bundle_key} nazev={it.nazev} parts={len(it.parts)} L={it.pocet_hodin}")
    print("Nesloučené úlohy:")
    for i, u in enumerate(x for x in plan_items if not hasattr(x, 'parts')):
        print(i + 1, u.id_tridy, u.nazev, u.puleny)




