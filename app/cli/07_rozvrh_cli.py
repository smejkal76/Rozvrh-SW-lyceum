"""
    Krok 6. Generování rozvrhu.
"""

from app.database import SessionLocal
from app.models.omezeni import CasoveOmezeniUcebny, CasoveOmezeniUcitele, DenEnum
from app.generator.calendars import Calendars, DAYS
from app.generator.tasks import build_tasks, group_halves, Uloha
from app.generator.sort_tasks import sort_items
from app.generator.engine import RozvrhGenerator
import random


def load_constraints(sess, calendars):
    # učitelé
    for o in sess.query(CasoveOmezeniUcitele).all():
        calendars.mark_teacher(o.id_ucitele, o.den, o.hodina_od, o.delka)
    # učebny
    for o in sess.query(CasoveOmezeniUcebny).all():
        calendars.mark_room(o.id_ucebny, o.den, o.hodina_od, o.delka)


if __name__ == "__main__":
    # Krok 1. Připojení do DB
    session = SessionLocal()

    # Krok 2. Nahrání omezení učitělů a učeben do kalendářů
    cal = Calendars()
    load_constraints(session, cal)

    # Krok 3. Nahrání předmětů do úloh
    ulohy = build_tasks(session)
    print(f"[K3] Načteno úloh: {len(ulohy)}")

    # Krok 4. Spojení půlených hodin
    plan_items = group_halves(ulohy, strict_pairs=False)
    print(f"[K4] Plánovacích položek: {len(plan_items)} | svazků: {sum(hasattr(x,'parts') for x in plan_items)}")

    # Krok 5. Seřazení položek podle náročnosti umístění
    items = sort_items(cal, plan_items)
    print("[K5] Položky seřazeny.")

    # Krok 6. Generování rozvrhu
    max_restarts = 50
    rng = random.Random()
    best_placed = None

    for attempt in range(1, max_restarts + 1):
        rng.shuffle(items)  # náhodně přeuspořádá prvky sekvence "items" na místě
        cal = Calendars()
        load_constraints(session, cal)
        gen = RozvrhGenerator(cal, max_restarts=max_restarts, rng=rng)

        if gen.try_place_all(items):
            best_placed = gen.placed
            print(f"[K6] Rozvrh vygenerován v pokusu #{attempt}.")
            break
        else:
            print(f"[K6] Pokus #{attempt} neúspěšný – restartuji…")

    if best_placed is None:
        raise SystemExit("[K6] Nebylo nalezeno řešení v daném počtu restartů.")
