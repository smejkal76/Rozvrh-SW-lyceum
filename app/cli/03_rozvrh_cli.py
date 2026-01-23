"""
    Krok 2. Přidán zápis časových omezení učitelů a učeben do kalendářů blokací
"""

from app.database import SessionLocal
from app.models.ucitel import Ucitel
from app.models.omezeni import CasoveOmezeniUcebny, CasoveOmezeniUcitele, DenEnum
from app.generator.calendars import Calendars, DAYS

# Mapování DenEnum -> index 0..4
DAY_TO_IDX = {
    DenEnum.Po: 0,
    DenEnum.Ut: 1,
    DenEnum.St: 2,
    DenEnum.Ct: 3,
    DenEnum.Pa: 4,
}
def load_constraints(sess, calendars):
    # učitelé
    for o in sess.query(CasoveOmezeniUcitele).all():
        calendars.mark_teacher(o.id_ucitele, o.den, o.hodina_od, o.delka)
    # učebny
    for o in sess.query(CasoveOmezeniUcebny).all():
        calendars.mark_room(o.id_ucebny, o.den, o.hodina_od, o.delka)

if __name__ == "__main__":
    session = SessionLocal()

    cal = Calendars()
    load_constraints(session, cal)
    print("[K2] Omezení nahrána do kalendářů.")

    # Kontrolní výpis: pro každého učitele vypiš (jméno, den, seznam blokovaných hodin)
    print("[K2] Obsah kalendáře blokací (busy_ucitel):")
    for u in session.query(Ucitel).all():
        for den in DenEnum:
            hodiny = cal.busy_ucitel[(u.id, den)]
            tisknout = False
            for h in hodiny:
                if h: tisknout = True
            if tisknout:
                print(f"   - {u.prijmeni} | {DAYS[DAY_TO_IDX[den]]} | {hodiny}")
