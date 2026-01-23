"""
diagnostics.py – diagnostika kvality rozvrhu (DDL-aligned)

Tahle verze je sladěná s aktuálním DDL:
- tabulka `vyucovaci_hodina` NEMÁ sloupec delka,
- délka bloku je v `predmet.pocet_hodin`,
- pokud je jedna vyučovací hodina složená z více předmětů (půlené / paralelní),
  bereme MAX(pocet_hodin) (v ideálním případě je stejná pro všechny).

Diagnostika běží po uložení do DB a pracuje jen s DB (zdroj pravdy pro exporty).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.generator.calendars import DAYS, DAY_TO_IDX


@dataclass(frozen=True)
class GapSegment:
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1


@dataclass
class ClassDayGaps:
    trida: str
    den_idx: int
    occupied_hours: List[int]
    gaps: List[GapSegment]

    @property
    def den_name(self) -> str:
        return DAYS[self.den_idx] if 0 <= self.den_idx < len(DAYS) else str(self.den_idx)


def _rows_to_hours_map(rows: Iterable[tuple], H: int) -> Dict[Tuple[str, int], Set[int]]:
    out: Dict[Tuple[str, int], Set[int]] = {}
    for trida, den, hodina_od, delka in rows:
        den_idx = DAY_TO_IDX[str(den)]
        key = (str(trida), den_idx)
        hs = out.setdefault(key, set())
        h0 = int(hodina_od)
        L = int(delka)
        for h in range(h0, h0 + L):
            if 1 <= h <= H:
                hs.add(h)
    return out


def load_class_hours_from_db(session, H: int = 7) -> Dict[Tuple[str, int], Set[int]]:
    """Načte obsazené hodiny tříd z DB.

    DDL:
    - vyucovaci_hodina: (id, nazev, den, hodina_od)
    - predmet: obsahuje `pocet_hodin` a odkaz `id_hodiny`

    Pokud je v jedné `id_hodiny` více předmětů (půlené), vezmeme MAX(pocet_hodin).

    Vrací mapu: (nazev_tridy, den_idx) -> set hodin.
    """

    q = text(
        """
        SELECT
            t.nazev AS trida,
            vh.den AS den,
            vh.hodina_od AS hodina_od,
            MAX(p.pocet_hodin) AS delka
        FROM predmet p
        JOIN trida t ON t.id = p.id_tridy
        JOIN vyucovaci_hodina vh ON vh.id = p.id_hodiny
        WHERE p.id_hodiny IS NOT NULL
        GROUP BY t.nazev, vh.den, vh.hodina_od
        ORDER BY
            vh.den,
            t.nazev,
            vh.hodina_od
        """
    )

    try:
        rows = session.execute(q).fetchall()
        return _rows_to_hours_map(rows, H=H)
    except ProgrammingError:
        # PostgreSQL: po chybě dotazu je transakce aborted
        session.rollback()
        raise


def compute_gaps_for_hours(hours: Set[int]) -> Tuple[List[int], List[GapSegment]]:
    """Z množiny obsazených hodin vypočte gap segmenty mezi první a poslední hodinou."""
    if not hours or len(hours) <= 1:
        occ_sorted = sorted(hours) if hours else []
        return occ_sorted, []

    occ_sorted = sorted(hours)
    first = occ_sorted[0]
    last = occ_sorted[-1]
    occ = set(occ_sorted)

    gaps: List[GapSegment] = []
    h = first
    while h <= last:
        if h in occ:
            h += 1
        else:
            gs = h
            while h <= last and h not in occ:
                h += 1
            ge = h - 1
            gaps.append(GapSegment(gs, ge))

    return occ_sorted, gaps


def build_gap_report(
    session,
    H: int = 7,
    include_tail: bool = False,
    tail_min_len: int = 2,
) -> List[ClassDayGaps]:
    """Postaví report mezer pro všechny třídy po dnech."""

    hours_map = load_class_hours_from_db(session, H=H)
    report: List[ClassDayGaps] = []

    for (cname, den_idx), hours in sorted(hours_map.items(), key=lambda x: (x[0][0], x[0][1])):
        occ_sorted, gaps = compute_gaps_for_hours(hours)

        if include_tail and occ_sorted:
            last = occ_sorted[-1]
            if last <= H - tail_min_len:
                gaps = gaps + [GapSegment(last + 1, H)]

        report.append(ClassDayGaps(trida=cname, den_idx=den_idx, occupied_hours=occ_sorted, gaps=gaps))

    return report


def print_gap_report(
    report: List[ClassDayGaps],
    log_multi_gaps: bool = True,
    log_gap_2plus: bool = True,
) -> None:
    """Vytiskne report mezer.

    - [GAPS] vypisuje dny s více než jednou mezerou
    - [GAP-2+] vypisuje každý souvislý gap délky >= 2
    """

    for r in report:
        if not r.gaps:
            continue

        gap_segments = [(g.start, g.end, g.length) for g in r.gaps]

        if log_multi_gaps and len(r.gaps) > 1:
            print(
                f"[GAPS] Třída {r.trida}, den {r.den_name}: "
                f"{len(r.gaps)} mezer {gap_segments}, hodiny {r.occupied_hours}"
            )

        if log_gap_2plus:
            for g in r.gaps:
                if g.length >= 2:
                    print(
                        f"[GAP-2+] Třída {r.trida}, den {r.den_name}: "
                        f"souvislá mezera {g.start}–{g.end} ({g.length} hod)"
                    )
