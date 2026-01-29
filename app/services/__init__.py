"""
    Potřebujeme to na něco?
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------- Datové struktury ----------

@dataclass
class HodinaView:
    """Jeden řádek z dotazu na rozvrh."""
    trida: str          # např. '10. Lyceum'
    den: str            # 'Po', 'Ut', 'St', 'Ct', 'Pa'
    hodina_od: int      # 1–7
    pocet_hodin: int    # délka bloku
    nazev_hodiny: str   # např. 'M', 'ČJ'
    ucitel: str         # např. 'Weise/Poprocký'


@dataclass
class DayMatrix:
    """Mřížka rozvrhu pro jeden den."""
    den: str                       # 'Po', 'Ut', ...
    tridy: List[str]              # seřazený seznam tříd (řádky)
    hodiny: List[int]             # seřazený seznam hodin (sloupce)
    # klíč = (třída, hodina_od), hodnota = text do buňky
    cells: Dict[Tuple[str, int], str]


# ---------- Načtení dat z DB ----------

_BASE_SQL = """
SELECT
    tr.nazev                             AS trida,
    vh.den                               AS den,
    vh.hodina_od                         AS hodina_od,
    MAX(p.pocet_hodin)                   AS pocet_hodin,
    vh.nazev                             AS nazev_hodiny,
    string_agg(u.prijmeni, '/')          AS ucitel
FROM predmet p
JOIN trida tr
  ON tr.id = p.id_tridy
JOIN ucitel u
  ON u.id = p.id_ucitele
JOIN vyucovaci_hodina vh
  ON vh.id = p.id_hodiny
WHERE p.id_hodiny IS NOT NULL
  {den_filter}
GROUP BY
    tr.nazev,
    vh.den,
    vh.hodina_od,
    vh.nazev
ORDER BY
    tr.nazev,
    vh.den,
    vh.hodina_od;
"""


def fetch_hodiny(session: Session, den: str | None = None) -> List[HodinaView]:
    """
    Vrátí plochý seznam hodin z DB.
    :param session: SQLAlchemy session
    :param den: volitelně filtrování na konkrétní den ('Po', 'Ut', 'St', 'Ct', 'Pa')
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
        m = row._mapping  # aby šlo přistupovat přes názvy sloupců
        hodiny.append(
            HodinaView(
                trida=m["trida"],
                den=m["den"],
                hodina_od=m["hodina_od"],
                pocet_hodin=m["pocet_hodin"],
                nazev_hodiny=m["nazev_hodiny"],
                ucitel=m["ucitel"],
            )
        )

    return hodiny


# ---------- Převod na matici pro jeden den ----------

def build_day_matrix(hodiny: List[HodinaView], den: str) -> DayMatrix:
    """
    Z plochého seznamu hodin poskládá matici pro daný den.

    Výsledek:
      - tridy = seřazený seznam tříd
      - hodiny = seřazený seznam začátků hodin
      - cells[(trida, hodina_od)] = text do buňky (předmět + učitel)
    """

    # filtrovat jen zvolený den (pro jistotu)
    hodiny_dne = [h for h in hodiny if h.den == den]

    if not hodiny_dne:
        return DayMatrix(den=den, tridy=[], hodiny=[], cells={})

    tridy = sorted({h.trida for h in hodiny_dne})
    hodiny_seznam = sorted({h.hodina_od for h in hodiny_dne})

    cells: Dict[Tuple[str, int], str] = {}
    for h in hodiny_dne:
        key = (h.trida, h.hodina_od)
        text_bunky = f"{h.nazev_hodiny}\n{h.ucitel}"
        # pokud by existovalo víc předmětů ve stejné buňce, prostě je spojíme
        if key in cells:
            cells[key] = cells[key] + " / " + text_bunky
        else:
            cells[key] = text_bunky

    return DayMatrix(
        den=den,
        tridy=tridy,
        hodiny=hodiny_seznam,
        cells=cells,
    )
