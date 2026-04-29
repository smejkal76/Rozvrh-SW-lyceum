from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session

@dataclass
class HodinySouhrn:
    trida: str
    zamereni: str
    celkem_hodin: int

@dataclass
class HodinyPivot:
    tridy: List[str]
    zamereni: List[str]
    data: Dict[str, Dict[str, int]]
    radky_soucet: Dict[str, int]
    sloupce_soucet: Dict[str, int]
    celkem: int

_HOURS_SQL = """
SELECT t.nazev AS trida, p.zamereni::text AS zamereni, SUM(p.pocet_hodin) AS celkem_hodin
FROM predmet p JOIN trida t ON t.id = p.id_tridy
GROUP BY t.nazev, p.zamereni ORDER BY t.nazev, p.zamereni;
"""

def fetch_hours_summary(session: Session) -> List[HodinySouhrn]:
    result = session.execute(text(_HOURS_SQL))
    rows: List[HodinySouhrn] = []
    for row in result:
        m = row._mapping
        rows.append(HodinySouhrn(trida=m["trida"], zamereni=m["zamereni"], celkem_hodin=int(m["celkem_hodin"])))
    return rows

def build_pivot(rows: List[HodinySouhrn]) -> HodinyPivot:
    tridy = sorted({r.trida for r in rows})
    zamereni = sorted({r.zamereni for r in rows})
    data: Dict[str, Dict[str, int]] = {t: {z: 0 for z in zamereni} for t in tridy}
    for r in rows:
        data[r.trida][r.zamereni] = r.celkem_hodin
    zamereni_spec = [z for z in zamereni if z != "vseobecny"]
    radky_soucet = {t: max((data[t][z] for z in zamereni_spec), default=0) + data[t].get("vseobecny", 0) for t in tridy}
    sloupce_soucet = {z: sum(data[t][z] for t in tridy) for z in zamereni}
    celkem = max((sloupce_soucet[z] for z in zamereni_spec), default=0) + sloupce_soucet.get("vseobecny", 0)
    return HodinyPivot(tridy=tridy, zamereni=zamereni, data=data, radky_soucet=radky_soucet, sloupce_soucet=sloupce_soucet, celkem=celkem)
