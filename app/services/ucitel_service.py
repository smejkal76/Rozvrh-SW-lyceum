from app.models.ucitel import Ucitel
from app.models.predmet import Predmet


def list_ucitele(db):
    return db.query(Ucitel).all()


def create_ucitel(db, jmeno, prijmeni):
    ucitel = Ucitel(prijmeni=prijmeni)
    db.add(ucitel)
    db.commit()


def delete_ucitel(db, ucitel_id):
    ucitel = db.query(Ucitel).filter(Ucitel.id == ucitel_id).first()

    if not ucitel:
        return False

    # 🔥 správná kontrola vazeb podle tvého modelu
    if db.query(Predmet).filter(Predmet.id_ucitele == ucitel_id).count() > 0:
        return False

    db.delete(ucitel)
    db.commit()
    return True