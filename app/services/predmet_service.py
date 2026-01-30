from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models.predmet import Predmet, ZamereniEnum
from app.models.ucitel import Ucitel


class PredmetService:
    """Služba pro správu předmětů."""

    @staticmethod
    def get_all_predmety(db: Session) -> list:
        """Vrátí seznam všech předmětů."""
        return db.execute(select(Predmet)).scalars().all()

    @staticmethod
    def get_predmet_by_id(db: Session, predmet_id: int):
        """Vrátí předmět podle ID."""
        return db.execute(
            select(Predmet).where(Predmet.id == predmet_id)
        ).scalar_one_or_none()

    @staticmethod
    def change_field(db: Session, predmet_id: int, field_name: str, new_value):
        """
        Změní jakékoliv pole u předmětu.

        Args:
            db: Session
            predmet_id: ID předmětu
            field_name: Název pole (id_ucitele, id_tridy, id_ucebny, id_hodiny, pocet_hodin, puleny, zamereni)
            new_value: Nová hodnota

        Raises:
            ValueError: Pokud předmět neexistuje
        """
        # Zkontroluj, že předmět existuje
        predmet = db.execute(
            select(Predmet).where(Predmet.id == predmet_id)
        ).scalar_one_or_none()

        if predmet is None:
            raise ValueError(f"Předmět s ID {predmet_id} neexistuje.")

        # Speciální ošetření pro zaměření (enum)
        if field_name == "zamereni":
            if isinstance(new_value, str):
                try:
                    new_value = ZamereniEnum[new_value]
                except KeyError:
                    raise ValueError(f"Neplatné zaměření: {new_value}")

        # Aktualizuj pole
        setattr(predmet, field_name, new_value)
        db.add(predmet)
        db.commit()
        db.refresh(predmet)

        return predmet

    @staticmethod
    def get_all_teachers(db: Session) -> list:
        """Vrátí seznam všech učitelů (abecedně)."""
        return db.execute(
            select(Ucitel).order_by(Ucitel.prijmeni)
        ).scalars().all()