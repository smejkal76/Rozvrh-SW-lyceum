from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


# ============================================================
# Datové struktury
# ============================================================

@dataclass
class HodinaView:
    """
    Jeden řádek rozvrhu (výsledek SQL dotazu).
    """
    trida: str           # např. '13 L'
    den: str             # 'Po', 'Ut', 'St', 'Ct', 'Pa'
    hodina_od: int       # začátek bloku (např. 2)
    pocet_hodin: int     # délka bloku (např. 2)
    nazev_hodiny: str    # např. 'M'
    ucitel: str          # např. 'Weise/Poprocký'


@dataclass
class DayMatrix:
    """
    Maticová reprezentace rozvrhu pro jeden den.
    """
    den: str
    tridy: List[str]                 # řádky
    hodiny: List[int]                # sloupce
    cells: Dict[Tuple[str, int], str]  # (třída, hodina) → text


# ============================================================
# SQL – zdroj dat
# ============================================================

_BASE_SQL = """
SELECT
    t.nazev                            AS trida,
    vh.den                             AS den,
    vh.hodina_od                       AS hodina_od,
    MAX(p.pocet_hodin)                 AS pocet_hodin,
    vh.nazev                           AS nazev_hodiny,
    string_agg(u.prijmeni, '/')        AS ucitel
FROM predmet p
JOIN trida t
  ON t.id = p.id_tridy
JOIN ucitel u
  ON u.id = p.id_ucitele
JOIN vyucovaci_hodina vh
  ON vh.id = p.id_hodiny
WHERE p.id_hodiny IS NOT NULL
  {den_filter}
GROUP BY
    t.nazev,
    vh.den,
    vh.hodina_od,
    vh.nazev
ORDER BY
    t.nazev,
    vh.den,
    vh.hodina_od;
"""


def fetch_hodiny(session: Session, den: str | None = None) -> List[HodinaView]:
    """
    Načte plochý seznam hodin z DB.
    """
    den_filter = ""
    params: dict = {}

    if den is not None:
        den_filter = "AND vh.den = :den"
        params["den"] = den

    sql = _BASE_SQL.format(den_filter=den_filter)
    result = session.execute(text(sql), params)

    hodiny: List[HodinaView] = []
    for row in result:
        m = row._mapping
        hodiny.append(
            HodinaView(
                trida=m["trida"],
                den=m["den"],
                hodina_od=int(m["hodina_od"]),
                pocet_hodin=int(m["pocet_hodin"]),
                nazev_hodiny=m["nazev_hodiny"],
                ucitel=m["ucitel"],
            )
        )

    return hodiny

# ============================================================
# Převod na matici (OPRAVENÁ LOGIKA BLOKŮ)
# ============================================================

def build_day_matrix(
    hodiny: List[HodinaView],
    den: str,
    all_hours: List[int],
) -> DayMatrix:
    """
    Z plochých dat sestaví matici pro jeden den.
    - Správně rozepíná bloky (pocet_hodin > 1)
    - Zobrazí i hodiny bez výuky (pauzy, oběd)
    """

    hodiny_dne = [h for h in hodiny if h.den == den]

    tridy = sorted({h.trida for h in hodiny_dne})
    cells: Dict[Tuple[str, int], str] = {}

    for h in hodiny_dne:
        text_cell = f"{h.nazev_hodiny}\n{h.ucitel}"

        for offset in range(max(1, h.pocet_hodin)):
            hh = h.hodina_od + offset
            key = (h.trida, hh)

            value = text_cell if offset == 0 else "↳ " + text_cell.replace("\n", " / ")
            cells[key] = value

    return DayMatrix(
        den=den,
        tridy=tridy,
        hodiny=all_hours,
        cells=cells,
    )


from sqlalchemy.orm import Session
from app.models.casove_omezeni_ucitele import CasoveOmezeniUcitele


def list_teacher_constraints(session: Session, teacher_id=None):

    q = session.query(CasoveOmezeniUcitele)

    if teacher_id:
        q = q.filter(CasoveOmezeniUcitele.id_ucitele == teacher_id)

    return q.all()


def create_teacher_constraint(
        session: Session,
        id_ucitele: int,
        den,
        hodina_od: int,
        delka: int):

    obj = CasoveOmezeniUcitele(
        id_ucitele=id_ucitele,
        den=den,
        hodina_od=hodina_od,
        delka=delka
    )

    session.add(obj)
    session.commit()

    return obj


def delete_teacher_constraint(session: Session, constraint_id: int):

    obj = session.get(CasoveOmezeniUcitele, constraint_id)

    if obj:
        session.delete(obj)
        session.commit()

from app.models.casove_omezeni_ucitele import CasoveOmezeniUcitele


def load_teacher_constraints(session):

    rows = session.query(CasoveOmezeniUcitele).all()

    busy = {}

    for r in rows:

        key = (r.id_ucitele, r.den.value)

        if key not in busy:
            busy[key] = {}

        for i in range(r.delka):

            h = r.hodina_od + i

            busy[key][h] = True

    return busy

def teacher_free(busy, teacher_id, day, hour):

    key = (teacher_id, day)

    if key not in busy:
        return True

    if hour in busy[key]:
        return False

    return True

    if not teacher_free(busy_ucitel, teacher_id, day, hour):
        return

def load_constraints(session, busy_ucitel, H):
    rows = session.execute("""
        SELECT id_ucitele, den, hodina_od, delka
        FROM casove_omezeni_ucitele
    """).fetchall()

    for r in rows:
        for h in range(r.hodina_od, r.hodina_od + r.delka):
            busy_ucitel[(r.id_ucitele, r.den)][h] = True

        if self.busy_ucitel[(ucitel, den)][h]:
            return False