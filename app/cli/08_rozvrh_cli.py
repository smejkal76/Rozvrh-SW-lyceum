"""
08_rozvrh_cli.py – CLI pro generování rozvrhu

CLI dělá jen:
- načtení dat a omezení,
- vygenerování rozvrhu s restarty,
- uložení do DB.

Diagnostika kvality (mezery apod.) je přesunuta do app/generator/diagnostics.py
aby běžela nad DB jako jediným zdrojem pravdy (a nepletla se do CLI).
"""

from __future__ import annotations

import random

from app.database import SessionLocal
from app.generator.calendars import Calendars
from app.generator.engine import RozvrhGenerator
from app.generator.persist import commit_schedule
from app.generator.tasks import build_tasks, group_halves
from app.generator.sort_tasks import sort_items
from app.models.omezeni import (
    CasoveOmezeniUcebny,
    CasoveOmezeniUcitele,
    CasoveOmezeniRozvrhu,
)
from app.models.trida import Trida


def load_constraints(sess, calendars: Calendars) -> None:
    """Naplní kalendáře časovými omezeními z DB.

    - CasoveOmezeniUcitele → busy_ucitel,
    - CasoveOmezeniUcebny → busy_ucebna,
    - CasoveOmezeniRozvrhu → block_trida (globální blokace pro všechny třídy).
    """
    for o in sess.query(CasoveOmezeniUcitele).all():
        calendars.mark_teacher(o.id_ucitele, o.den, o.hodina_od, o.delka)

    for o in sess.query(CasoveOmezeniUcebny).all():
        calendars.mark_room(o.id_ucebny, o.den, o.hodina_od, o.delka)

    tridy = sess.query(Trida).all()
    for o in sess.query(CasoveOmezeniRozvrhu).all():
        for trida in tridy:
            calendars.mark_class_block(trida.id, o.den, o.hodina_od, o.delka)


if __name__ == "__main__":
    session = SessionLocal()

    # omezení pro sort_items (difficulty)
    base_cal = Calendars()
    load_constraints(session, base_cal)

    # úlohy
    ulohy = build_tasks(session)
    print(f"[K3] Načteno úloh: {len(ulohy)}")

    # svazky/půlenky
    plan_items = group_halves(ulohy, strict_pairs=False)
    print(
        f"[K4] Plánovacích položek: {len(plan_items)} | "
        f"svazků: {sum(hasattr(x, 'parts') for x in plan_items)}"
    )

    # seřazení
    items = sort_items(base_cal, plan_items)
    print("[K5] Položky seřazeny.")

    # generování
    max_restarts = 50
    rng = random.Random()
    best_placed = None

    for attempt in range(1, max_restarts + 1):
        rng.shuffle(items)
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

    inserted = commit_schedule(session, best_placed, clear_before=True)
    print(
        f"[K7] Zapsáno {inserted} vyucovaci_hodina a nastaveno id_hodiny v predmetech."
    )

    # Diagnostika je mimo CLI:
    from app.generator.diagnostics import build_gap_report, print_gap_report
    report = build_gap_report(session, H=base_cal.H, include_tail=False)
    print_gap_report(report)
