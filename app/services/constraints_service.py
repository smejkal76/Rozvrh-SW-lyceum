from sqlalchemy.orm import Session
from app.models.omezeni import CasoveOmezeniRozvrhu

def get_all_omezeni_rozvrhu(db: Session):
    """Načte všechna časová omezení rozvrhu z DB."""
    return db.query(CasoveOmezeniRozvrhu).order_by(
        CasoveOmezeniRozvrhu.den,
        CasoveOmezeniRozvrhu.hodina_od
    ).all()

def add_omezeni_rozvrhu(db: Session, nazev: str, den: str, hodina_od: int, delka: int):
    """Přidá nové časové omezení rozvrhu do DB."""
    omezeni = CasoveOmezeniRozvrhu(
        nazev=nazev,
        den=den,
        hodina_od=hodina_od,
        delka=delka
    )
    db.add(omezeni)
    db.commit()
    db.refresh(omezeni)
    return omezeni

def delete_omezeni_rozvrhu(db: Session, omezeni_id: int):
    """Smaže časové omezení rozvrhu podle ID."""
    omezeni = db.query(CasoveOmezeniRozvrhu).filter(
        CasoveOmezeniRozvrhu.id == omezeni_id
    ).first()
    if omezeni:
        db.delete(omezeni)
        db.commit()
    return omezeni