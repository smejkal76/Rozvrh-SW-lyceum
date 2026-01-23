"""
generator/tasks.py

Krok 3 a 4. runtime datové modely a seskupování půlených hodin

Uloha je minimální, ORM‑nezávislý runtime snapshot jedné vyučovací jednotky (třída/učitel/učebna/délka + příznak půlení,
zaměření a název předmětu). Obsahuje tedy i nazev, který se používá pro srozumitelný výpis a později pro generování
názvů hodin.

SloucenaUloha reprezentuje paralelní dvojici půlených hodin, které musí běžet současně ve stejném (den, start).
Invariant: len(parts) == 2 a obě části mají shodný pocet_hodin. Navíc ukládá nazev, který je složen ze jmen obou částí
ve tvaru u1.nazev/u2.nazev.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict, deque
from typing import List, Tuple, Dict, Optional, Deque

from app.models.predmet import Predmet

__all__ = ["Uloha", "SloucenaUloha", "group_halves"]


# POZN.: ZamereniEnum je Enum v ORM modelu Predmet; hodnotu převedeme na str/None
def _norm_zamereni(z) -> Optional[str]:
    """ZamereniEnum -> Optional[str]. 'vseobecny' bereme jako None."""
    if z is None:
        return None
    val = getattr(z, "value", z)   # Enum nebo string
    return None if str(val) == "vseobecny" else str(val)

@dataclass(slots=True)
class Uloha:
    """Minimální vstupní jednotka pro rozvrhovací engine.

    Atributy
    --------
    id_predmetu : int
        Primární klíč z tabulky `predmet` (pro zápis do vyucovaci_hodina).
    id_tridy : int
        Kolizní zdroj – třída.
    id_ucitele : int
        Kolizní zdroj – učitel.
    id_ucebny : int | None
        Kolizní zdroj – učebna (pokud je pevně daná). None = libovolná/nezadaná.
    pocet_hodin : int
        Délka bloku v hodinách (souvisle).
    puleny : bool
        True, pokud je předmět označen jako půlený (kandidát na paralelní svazek).
    zamereni : str
        Textový klíč zaměření (např. "vseobecny" | "humanitni" | "prirodovedny").
    """

    id_predmetu: int
    id_tridy: int
    id_ucitele: int
    id_ucebny: int
    pocet_hodin: int
    puleny: bool
    zamereni: str  # 'vseobecny' | 'humanitni' | 'prirodovedny'
    nazev: str

# ---------------------------------------------
# Načtení úloh z DB → list[Uloha]
# ---------------------------------------------

def build_tasks(sess):
    """Načti `Predmet` a vytvoř `Uloha` vč. puleny+zamereni.
    Sloupce: id, zkratka, zamereni (Enum), puleny (bool), pocet_hodin, id_tridy, id_ucitele, id_ucebny.
    """
    ulohy: list[Uloha] = []
    for p in sess.query(Predmet).all():
        if p.pocet_hodin < 1:
            raise ValueError(f"Predmet {p.id}: pocet_hodin musí být >=1")
        ulohy.append(Uloha(
            id_predmetu=p.id,
            id_tridy=p.id_tridy,
            id_ucitele=p.id_ucitele,
            id_ucebny=p.id_ucebny,
            pocet_hodin=int(p.pocet_hodin),
            puleny=bool(p.puleny),
            zamereni=_norm_zamereni(getattr(p, "zamereni", None)),
            nazev=str(p.nazev),
        ))
    return ulohy

@dataclass(slots=True)
class SloucenaUloha:
    """Paralelní dvojice půlených hodin (běží současně).
        Invarianty: len(parts) == 2, všechny části mají shodný pocet_hodin.
        bundle_key slouží pro debug: (id_tridy, zamereni, pocet_hodin).
        Nazev je složen jako 'u1.nazev/u2.nazev'.
    """
    parts: List[Uloha]      # přesně dvě položky Uloha
    pocet_hodin: int        # délka bloku
    bundle_key: Tuple[int, str, int]
    nazev: str


# Pravidla pro slučování předmětů: různé názvy, různí učitelé, různé učebny
def _compatible(u1: Uloha, u2: Uloha) -> bool:
    # 1) různé názvy
    if u1.nazev == u2.nazev:
        return False
    # 2) různí učitelé
    if u1.id_ucitele == u2.id_ucitele:
        return False
    # 3) různé pevně dané učebny (pokud jsou obě zadané)
    if (u1.id_ucebny is not None) and (u2.id_ucebny is not None) and (u1.id_ucebny == u2.id_ucebny):
        return False
    return True

# určení "zaměření" páru do bundle_key
def _pair_focus(z1: str, z2: str) -> str:
    if z1 == 'vseobecny' and z2 == 'vseobecny':
        return 'vseobecny'
    return 'zamereni'


def group_halves(
    ulohy: List[Uloha],
    strict_pairs: bool = True  # True = vyžaduj páry; False = zbytky nech single
) -> List[Uloha | SloucenaUloha]:
    """Vytvoř paralelní dvojice půlených hodin uvnitř stejné třídy a stejné délky.

    Pravidla:
      - 'vseobecny' ↔ 'vseobecny', speciální ↔ jiný speciální (různá zaměření),
      - ve dvojici různé názvy předmětů a (pokud obě pevné) různé učebny,
      - výsledný `bundle_key` má tvar (id_tridy, zamereni_páru, pocet_hodin).
    """

    singles: List[Uloha] = []   # list NEPŮLENÝCH úloh, 1. část návratové hodnoty funkce
    by_bucket: Dict[Tuple[int, int], List[Uloha]] = defaultdict(list) # PŮLENÉ úlohy: kbelíky podle (třída, délka) —
                                                                      # NE podle zaměření, aby šlo párovat různá
                                                                      # zaměření

    # rozdělení na půlené a nepůlené
    for u in ulohy:
        if not u.puleny:
            singles.append(u)
        else:
            z = u.zamereni or 'vseobecny'
            by_bucket[(u.id_tridy, u.pocet_hodin)].append(u)
    # tímto máme nepůlené hotové

    # dále řešíme půlené -> sloučené
    bundles: List[SloucenaUloha] = []   # 2. část návratové hodnoty funkce

    # Iterace nepůlených přes skupiny (třída, délka hodiny).
    # V rámci těchto skupin dochází ke spojování.
    for (trida, L), items in by_bucket.items():
        # Na začátku úlohy s pevně danou učebnou, aby měly větší šanci se spojit, poté ostatní
        items.sort(key=lambda x: (x.id_ucebny is None, (x.zamereni or 'vseobecny'), (x.nazev or ''), x.id_predmetu))

        # rozdělit na "všeobecné" a "se zaměřením" topics
        general: Deque[Uloha] = deque()     # všeobecné
        topics: Dict[str, Deque[Uloha]] = defaultdict(deque)    # se zaměřením: str obsahuje název zaměření a každé
                                                                # zaměření kontejner úloh
        # rozdělení do skupin: všeobecný, přírodovědný, humanitní
        for u in items:
            z = u.zamereni or 'vseobecny'
            if z == 'vseobecny':
                general.append(u)
            else:
                topics[z].append(u)

        # 1) párování: speciální ↔ jiný speciální (různá zaměření)

        #
        def _largest_topic(d: Dict[str, Deque[Uloha]]):
            return max(d.keys(), key=lambda k: len(d[k])) if d else None

        while True:
            t1 = _largest_topic(topics)
            if t1 is None or sum(1 for q in topics.values() if q) < 2:
                break
            u1 = topics[t1].popleft()
            # zkus najít kompatibilní protějšek v jiných topicách
            found = None
            for t2, q in list(topics.items()):
                if t2 == t1 or not q:
                    continue
                for _ in range(len(q)):
                    cand = q.popleft()
                    if _compatible(u1, cand):
                        found = (t2, cand)
                        break
                    q.append(cand)
                if found:
                    break
            if not found:
                # vrať u1 zpět a skonči (další páry už nevzniknou)
                topics[t1].appendleft(u1)
                break
            t2, u2 = found
            # slož bundle_key se zaměřením páru = 'mix'
            bk = (trida, "zamereni", L)
            bundles.append(SloucenaUloha(parts=[u1, u2], pocet_hodin=L, bundle_key=bk, nazev=f"{u1.nazev}/{u2.nazev}"))
            if not topics[t1]:
                topics.pop(t1, None)
            if t2 in topics and not topics[t2]:
                topics.pop(t2, None)

        # 2) párování: všeobecný ↔ všeobecný
        # rotuj, dokud nenajdeš kompatibilní pár; zabráníme cyklení čítačem rotací
        rotated = 0
        while len(general) >= 2 and rotated < len(general):
            u1 = general.popleft()
            paired = False
            for _ in range(len(general)):
                u2 = general.popleft()
                if _compatible(u1, u2):
                    bk = (trida, "vseobecny", L)
                    bundles.append(SloucenaUloha(parts=[u1, u2], pocet_hodin=L, bundle_key=bk, nazev=f"{u1.nazev}/{u2.nazev}"))
                    paired = True
                    break
                else:
                    general.append(u2)
            if not paired:
                general.append(u1)
                rotated += 1
            else:
                rotated = 0

        # 3) nespojené zbytky
        leftovers: List[Uloha] = list(general)
        for q in topics.values():
            leftovers.extend(list(q))
        if leftovers:
            if strict_pairs:
                ids = ", ".join(f"predmet#{u.id_predmetu}" for u in leftovers)
                raise ValueError(
                    f"Nelze spárovat půlené hodiny v koši (trida={trida}, L={L}): {ids}. "
                    f"Chybí protějšky (jiné zaměření u speciálních nebo kompatibilní název/učebna)."
                )
            else:
                # připojení nespojených k nepůleným
                singles.extend(leftovers)

    return singles + bundles