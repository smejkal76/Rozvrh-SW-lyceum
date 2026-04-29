from app.models.ucitel import Ucitel
from app.models.predmet import Predmet




# app/services/omezeni_ucitele_service.py

from app.models.casove_omezeni_ucitele import CasoveOmezeniUcitel


def list_omezeni_ucitele(session):
    return session.query(CasoveOmezeniUcitel).all()


def get_omezeni_ucitele(session, omezeni_id):
    return session.query(CasoveOmezeniUcitel).filter(
        CasoveOmezeniUcitel.id == omezeni_id
    ).first()


def create_omezeni_ucitele(session, id_ucitele, den, hodina_od, delka):
    obj = CasoveOmezeniUcitel(
        id_ucitele=id_ucitele,
        den=den,
        hodina_od=hodina_od,
        delka=delka
    )
    session.add(obj)
    session.commit()
    return obj


def delete_omezeni_ucitele(session, omezeni_id):
    obj = get_omezeni_ucitele(session, omezeni_id)
    if obj:
        session.delete(obj)
        session.commit()