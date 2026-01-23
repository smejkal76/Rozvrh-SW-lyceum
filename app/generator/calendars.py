"""
calendars.py – kalendáře obsazenosti pro generátor rozvrhu

Odděluje:
- reálné naplánované hodiny tříd (busy_trida),
- časová omezení rozvrhu (block_trida, např. casove_omezeni_rozvrhu),
- obsazenost učitelů a učeben (busy_ucitel, busy_ucebna).

Indexace hodin je 1..H, index 0 v řádcích se nepoužívá.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.models.omezeni import DenEnum

# Mapování dny v týdnu
DAY_TO_IDX: Dict[str, int] = {"Po": 0, "Ut": 1, "St": 2, "Ct": 3, "Pa": 4}
IDX_TO_DAY: Dict[int, str] = {v: k for k, v in DAY_TO_IDX.items()}
DAYS = ["Po", "Ut", "St", "Ct", "Pa"]


def _norm_day(den) -> DenEnum:
    """Normalizuje den na DenEnum.

    Přijme DenEnum | int (0..4) | str ('Po'..'Pa').
    """
    if isinstance(den, DenEnum):
        return den
    if isinstance(den, int):
        m = {0: DenEnum.Po, 1: DenEnum.Ut, 2: DenEnum.St, 3: DenEnum.Ct, 4: DenEnum.Pa}
        return m[den]
    if isinstance(den, str):
        s = den.strip()
        m = {"Po": DenEnum.Po, "Ut": DenEnum.Ut, "St": DenEnum.St, "Ct": DenEnum.Ct, "Pa": DenEnum.Pa}
        return m[s]
    raise TypeError(f"Neznámý typ dne: {type(den)} -> {den}")


class Calendars:
    """Jednoduché kalendáře obsazenosti.

    Všechny mapy (busy_*/block_*) vrací list[bool] délky H+1 pro každý klíč
    (index 0 se nepoužívá, 1..H jsou jednotlivé hodiny).
    """

    def __init__(self, H: int = 7, D: int = 5) -> None:
        self.H = H
        self.D = D

        # reálné naplánované hodiny tříd
        self.busy_trida = defaultdict(lambda: [False] * (H + 1))
        # blokace (casove_omezeni_rozvrhu)
        self.block_trida = defaultdict(lambda: [False] * (H + 1))

        # učitelé a učebny – mix skutečných hodin a jejich omezení
        self.busy_ucitel = defaultdict(lambda: [False] * (H + 1))
        self.busy_ucebna = defaultdict(lambda: [False] * (H + 1))

    # ------------------------------------------------------------------
    # Značení obsazenosti
    # ------------------------------------------------------------------
    def _mark(self, arr: List[bool], start: int, length: int) -> None:
        """Označí blok [start, start+length-1] jako obsazený (1..H)."""
        if length <= 0:
            return
        # ochrana proti přestřelení hranic
        s = max(1, start)
        e = min(self.H, start + length - 1)
        for h in range(s, e + 1):
            arr[h] = True

    def mark_teacher(self, id_ucitele: int, den, start: int, length: int) -> None:
        d = _norm_day(den)
        self._mark(self.busy_ucitel[(id_ucitele, d)], start, length)

    def mark_room(self, id_ucebny: int, den, start: int, length: int) -> None:
        d = _norm_day(den)
        self._mark(self.busy_ucebna[(id_ucebny, d)], start, length)

    # reálné hodiny třídy
    def mark_class(self, id_tridy: int, den, start: int, length: int) -> None:
        d = _norm_day(den)
        self._mark(self.busy_trida[(id_tridy, d)], start, length)

    # blokace pro třídu (casove_omezeni_rozvrhu)
    def mark_class_block(self, id_tridy: int, den, start: int, length: int) -> None:
        d = _norm_day(den)
        self._mark(self.block_trida[(id_tridy, d)], start, length)

    # ------------------------------------------------------------------
    # Dotazy na obsazenost
    # ------------------------------------------------------------------
    def is_free_teacher(self, id_ucitele: int, den, start: int, length: int) -> bool:
        d = _norm_day(den)
        row = self.busy_ucitel[(id_ucitele, d)]
        end = start + length
        upper = min(self.H, len(row) - 1)
        if start < 1 or end - 1 > upper:
            return False
        return not any(row[h] for h in range(start, end))

    def is_free_room(self, id_ucebny: int, den, start: int, length: int) -> bool:
        d = _norm_day(den)
        row = self.busy_ucebna[(id_ucebny, d)]
        end = start + length
        upper = min(self.H, len(row) - 1)
        if start < 1 or end - 1 > upper:
            return False
        return not any(row[h] for h in range(start, end))

    def is_free_class(self, id_tridy: int, den, start: int, length: int) -> bool:
        """Volnost třídy – bere v úvahu busy_trida i block_trida."""
        d = _norm_day(den)
        busy = self.busy_trida[(id_tridy, d)]
        block = self.block_trida[(id_tridy, d)]
        end = start + length
        upper = min(self.H, len(busy) - 1, len(block) - 1)
        if start < 1 or end - 1 > upper:
            return False
        return not any(busy[h] or block[h] for h in range(start, end))

    # pro výpočty zátěže / děr tříd (pouze reálné hodiny)
    def class_busy_row(self, id_tridy: int, den_idx: int) -> List[bool]:
        d = _norm_day(den_idx)
        return self.busy_trida[(id_tridy, d)]

    # ------------------------------------------------------------------
    # Debug výpisy
    # ------------------------------------------------------------------
    def _debug_print_row(self, label: str, row: List[bool]) -> None:
        buf = ["X" if row[h] else "." for h in range(1, self.H + 1)]
        print(label, ":", "".join(buf))

    def debug_print_teacher_day(self, id_ucitele: int, den_idx: int) -> None:
        d = _norm_day(den_idx)
        row = self.busy_ucitel[(id_ucitele, d)]
        self._debug_print_row(f"Učitel#{id_ucitele} {DAYS[den_idx]}", row)

    def debug_print_room_day(self, id_ucebny: int, den_idx: int) -> None:
        d = _norm_day(den_idx)
        row = self.busy_ucebna[(id_ucebny, d)]
        self._debug_print_row(f"Učebna#{id_ucebny} {DAYS[den_idx]}", row)

    def debug_print_class_day(self, id_tridy: int, den_idx: int) -> None:
        row = self.class_busy_row(id_tridy, den_idx)
        self._debug_print_row(f"Třída#{id_tridy} {DAYS[den_idx]}", row)
