from app.models.ucebna import Ucebna
from app.models.predmet import Predmet

def list_ucebna(session):
    return session.query(Ucebna).order_by(Ucebna.nazev).all()

def get_ucebna(session, ucebna_id):
    return session.query(Ucebna).filter(Ucebna.id == ucebna_id).first()

def create_ucebna(session, nazev):
    existing = session.query(Ucebna).filter(Ucebna.nazev == nazev).first()
    if existing:
        raise ValueError(f'Učebna "{nazev}" již existuje.')
    ucebna = Ucebna(nazev=nazev)
    session.add(ucebna)
    session.commit()
    return ucebna

def update_ucebna(session, ucebna_id, nazev):
    ucebna = get_ucebna(session, ucebna_id)
    if not ucebna:
        raise ValueError('Učebna nenalezena.')
    existing = session.query(Ucebna)\
        .filter(Ucebna.nazev == nazev, Ucebna.id != ucebna_id).first()
    if existing:
        raise ValueError(f'Název "{nazev}" je již použit.')
    ucebna.nazev = nazev
    session.commit()
    return ucebna

def delete_ucebna(session, ucebna_id):
    ucebna = get_ucebna(session, ucebna_id)
    if not ucebna:
        raise ValueError('Učebna nenalezena.')
    vazby = session.query(Predmet)\
        .filter(Predmet.id_ucebny == ucebna_id).count()
    if vazby > 0:
        raise ValueError(
            f'Nelze smazat: učebna je přiřazena k {vazby} předmět(ům).')
    session.delete(ucebna)
    session.commit()