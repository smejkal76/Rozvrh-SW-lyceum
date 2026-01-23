"""
    generator/persist.py

    Krok 7. Uložení vygenerovaného rozvrhu do DB.

    Po úspěšném umístění (Krok 6) zapíšeme výsledek do databáze, tabulky vyucovaci_hodina.
"""

from typing import Iterable
from sqlalchemy.orm import Session
from app.models.predmet import Predmet
from app.models.vyucovaci_hodina import VyucovaciHodina, DenEnum

IDX_TO_DENENUM = {
    0: DenEnum.Po,
    1: DenEnum.Ut,
    2: DenEnum.St,
    3: DenEnum.Ct,
    4: DenEnum.Pa,
}

def _insert_vh(sess: Session, nazev: str, den_idx: int, start: int) -> VyucovaciHodina:
    """Vloží jeden záznam do VYUCOVACI_HODINA."""
    rec = VyucovaciHodina(
        nazev=nazev,
        den=IDX_TO_DENENUM[den_idx],
        hodina_od=start
    )
    sess.add(rec)
    sess.flush()   # získáme rec.id bez commit
    return rec

def _link_predmet(sess: Session, predmet_id: int, vh_id: int) -> None:
    """Nastaví FK PREDMET.id_hodiny → vyucovaci_hodina.id"""
    sess.query(Predmet).filter(Predmet.id == predmet_id).update({Predmet.id_hodiny: vh_id})

def commit_schedule(sess: Session, placed: Iterable[tuple], clear_before: bool = False) -> int:
    """
    Zapíše umístěné položky do DB.

    - Uloha → 1× VH + update PREDMET.id_hodiny
    - SloucenaUloha → 1× VH + update pro oba předměty

    Pokud clear_before=True:
      - smaže staré VH,
      - nastaví všem předmětům id_hodiny = NULL.

    Vrací počet vložených VH.
    """
    if clear_before:
        sess.query(Predmet).update({Predmet.id_hodiny: None})
        sess.query(VyucovaciHodina).delete()
        sess.commit()
        print("[K7] Vymazány předchozí záznamy rozvrhu.")

    rows = 0
    for (it, den_idx, start) in placed:
        # vytvoříme 1 vyučovací hodinu
        vh = _insert_vh(sess, nazev=it.nazev, den_idx=den_idx, start=start)

        if hasattr(it, "parts"):  # SloucenaUloha
            for u in it.parts:
                _link_predmet(sess, predmet_id=u.id_predmetu, vh_id=vh.id)
        else:                      # Uloha
            _link_predmet(sess, predmet_id=it.id_predmetu, vh_id=vh.id)

        rows += 1

    sess.commit()
    return rows