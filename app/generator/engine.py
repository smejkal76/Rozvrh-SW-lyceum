"""
engine.py – generátor rozvrhu

Střední refaktoring s:
- oddělením busy/block u tříd (využívá Calendars),
- tvrdým obědem (2–4 nesmí být všechny plné),
- tvrdým začátkem dne (první obsazená hodina musí být 1),
- globální podmínkou „žádný prázdný den pro třídu“,
- kvadratickou penalizací děr,
- vyvažováním zátěže tříd a učitelů přes dny.
"""

from __future__ import annotations

import random
from typing import Iterable, List, Tuple

from app.generator.tasks import Uloha, SloucenaUloha
from app.generator.calendars import Calendars
from app.models.omezeni import DenEnum

INF = 10 ** 12

IDX_TO_DENENUM = {
    0: DenEnum.Po,
    1: DenEnum.Ut,
    2: DenEnum.St,
    3: DenEnum.Ct,
    4: DenEnum.Pa,
}


class RozvrhGenerator:
    def __init__(self, calendars: Calendars, max_restarts: int = 50, rng: random.Random | None = None) -> None:
        self.cal = calendars
        self.max_restarts = max_restarts
        self.H = calendars.H    # Počet vedlejších vyučovacích hodin
        self.D = calendars.D    # Počet rozvrhovaných dní Po-Pá
        self.rng = rng or random.Random()

        self.placed: List[Tuple[Uloha | SloucenaUloha, int, int]] = []

        # váhy cost funkce
        self.W_BAL_CLASS = 3.0
        self.W_BAL_TEACH = 2.0
        self.W_LUNCH_HARD = 100.0
        self.W_EDGE_BONUS = 0.0
        self.W_GAPS = 3.0
        self.W_LATE = 1.0

    # ------------------------------------------------------------------
    # Označení obsazenosti
    # ------------------------------------------------------------------
    def _mark_single(self, u: Uloha, den_idx: int, start: int) -> None:
        dkey = IDX_TO_DENENUM[den_idx]
        L = u.pocet_hodin
        # třída – reálné hodiny
        self.cal.mark_class(u.id_tridy, dkey, start, L)
        # učitel
        if getattr(u, "id_ucitele", None) is not None:
            self.cal.mark_teacher(u.id_ucitele, dkey, start, L)
        # učebna
        if getattr(u, "id_ucebny", None):
            self.cal.mark_room(u.id_ucebny, dkey, start, L)

    # ------------------------------------------------------------------
    # Kontroly volnosti – tvrdá omezení
    # ------------------------------------------------------------------
    def _free_single(self, u: Uloha, den_idx: int, start: int) -> bool:
        dkey = IDX_TO_DENENUM[den_idx]
        L = u.pocet_hodin
        end = start + L

        # třída – reálné hodiny i blokace
        busy_tr = self.cal.busy_trida[(u.id_tridy, dkey)]
        block_tr = self.cal.block_trida[(u.id_tridy, dkey)]
        lim_tr = min(self.H, len(busy_tr) - 1, len(block_tr) - 1)

        # učitel (může být None)
        te_row = None
        if getattr(u, "id_ucitele", None) is not None:
            te_row = self.cal.busy_ucitel[(u.id_ucitele, dkey)]
            lim_te = min(self.H, len(te_row) - 1)
        else:
            lim_te = self.H

        lim = min(lim_tr, lim_te)

        if start < 1 or end - 1 > lim:
            return False

        # třída – nesmí mít v intervalu ani reálnou hodinu, ani blokaci
        if any(busy_tr[h] or block_tr[h] for h in range(start, end)):
            return False

        # učitel – nesmí mít jinou hodinu v intervalu
        if te_row is not None and any(te_row[h] for h in range(start, end)):
            return False

        # učebna
        if getattr(u, "id_ucebny", None):
            rm_row = self.cal.busy_ucebna[(u.id_ucebny, dkey)]
            lim_rm = min(self.H, len(rm_row) - 1)
            lim2 = min(lim, lim_rm)
            if end - 1 > lim2:
                return False
            if any(rm_row[h] for h in range(start, end)):
                return False

        return True

    def free(self, item: Uloha | SloucenaUloha, den_idx: int, start: int) -> bool:
        parts = item.parts if hasattr(item, "parts") else [item]
        return all(self._free_single(u, den_idx, start) for u in parts)

    # ------------------------------------------------------------------
    # Zátěže
    # ------------------------------------------------------------------
    def _row_sum(self, row: list[bool]) -> int:
        upper = min(self.H, len(row) - 1)
        return sum(1 for h in range(1, upper + 1) if row[h])

    def _class_load_day(self, id_tridy: int, den_idx: int) -> int:
        row = self.cal.class_busy_row(id_tridy, den_idx)
        return self._row_sum(row)

    def _teach_load_day(self, id_ucitele: int, den_idx: int) -> int:
        dkey = IDX_TO_DENENUM[den_idx]
        row = self.cal.busy_ucitel[(id_ucitele, dkey)]
        return self._row_sum(row)

    # ------------------------------------------------------------------
    # Oběd (2,3,4 nesmí být všechny plné)
    # ------------------------------------------------------------------
    def _lunch_violation(self, row: list[bool], start: int, L: int) -> bool:
        """True, pokud po nasimulování bloku budou 2,3,4 všechny obsazené."""
        tmp = row[:]
        for h in range(start, start + L):
            if 1 <= h <= self.H and h < len(tmp):
                tmp[h] = True
        return all((len(tmp) > x and tmp[x]) for x in (2, 3, 4) if x <= self.H)

    # ------------------------------------------------------------------
    # Cost funkce
    # ------------------------------------------------------------------
    def _placement_cost(self, item: Uloha | SloucenaUloha, den_idx: int, start: int) -> float:
        if not self.free(item, den_idx, start):
            return INF

        parts = item.parts if hasattr(item, "parts") else [item]
        L = parts[0].pocet_hodin
        id_tridy = parts[0].id_tridy

        cost = 0.0

        # vyrovnanost tříd
        before_class = self._class_load_day(id_tridy, den_idx)
        after_class = before_class + L
        cost += self.W_BAL_CLASS * (after_class**2 - before_class**2)

        # vyrovnanost učitelů
        for u in parts:
            if getattr(u, "id_ucitele", None) is None:
                continue
            before_t = self._teach_load_day(u.id_ucitele, den_idx)
            after_t = before_t + L
            cost += self.W_BAL_TEACH * (after_t**2 - before_t**2)

        # oběd – tvrdé omezení
        dkey = IDX_TO_DENENUM[den_idx]
        class_row = self.cal.busy_trida[(id_tridy, dkey)]
        if self._lunch_violation(class_row, start, L):
            return INF

        # kompaktnost dne (jen reálné hodiny třídy)
        tmp = class_row[:]
        for h in range(start, start + L):
            if 1 <= h <= self.H and h < len(tmp):
                tmp[h] = True

        upper = min(self.H, len(tmp) - 1)
        occupied = [h for h in range(1, upper + 1) if tmp[h]]
        if occupied:
            first = occupied[0]
            last = occupied[-1]
            holes = (last - first + 1) - len(occupied)
            late = max(0, first - 1)

            # den s výukou musí začínat 1. hodinou
            if first != 1:
                return INF

            # díry – kvadratická penalizace
            cost += self.W_GAPS * (holes**2)
            cost += self.W_LATE * late

        # drobný šum, aby při shodném costu nevznikal deterministický vzor
        cost += self.rng.randint(0, 3)
        return cost

    # ------------------------------------------------------------------
    # Generování slotů
    # ------------------------------------------------------------------
    def _iter_slots(self, L: int) -> Iterable[Tuple[int, int]]:
        days = list(range(self.D))
        self.rng.shuffle(days)
        for d in days:
            starts = list(range(1, self.H - L + 2))
            self.rng.shuffle(starts)
            for s in starts:
                yield d, s

    # ------------------------------------------------------------------
    # Globální podmínka – žádný prázdný den
    # ------------------------------------------------------------------
    def _all_classes_have_lessons_each_day(self) -> bool:
        class_ids = set()
        for item, den_idx, start in self.placed:
            parts = item.parts if hasattr(item, "parts") else [item]
            for u in parts:
                class_ids.add(u.id_tridy)

        for cid in class_ids:
            for d in range(self.D):
                if self._class_load_day(cid, d) == 0:
                    return False
        return True

    # ------------------------------------------------------------------
    # Veřejné API
    # ------------------------------------------------------------------
    def place(self, item: Uloha | SloucenaUloha, den_idx: int, start: int) -> None:
        parts = item.parts if hasattr(item, "parts") else [item]
        for u in parts:
            self._mark_single(u, den_idx, start)
        self.placed.append((item, den_idx, start))

    def try_place_all(self, items: List[Uloha | SloucenaUloha]) -> bool:
        self.placed.clear()

        for it in items:
            best_cost = INF
            best_d = None
            best_s = None

            for d, s in self._iter_slots(it.pocet_hodin):
                c = self._placement_cost(it, d, s)
                if c < best_cost:
                    best_cost = c
                    best_d = d
                    best_s = s

            if best_d is None:
                return False

            self.place(it, best_d, best_s)

        if not self._all_classes_have_lessons_each_day():
            return False

        return True
