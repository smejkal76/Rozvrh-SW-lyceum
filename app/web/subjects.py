from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import SessionLocal
from app.models.predmet import Predmet
from app.models.ucitel import Ucitel
from app.models.trida import Trida
from app.models.ucebna import Ucebna
from app.models.vyucovaci_hodina import VyucovaciHodina
from app.services.predmet_service import PredmetService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/view/edit/subjects", response_class=HTMLResponse)
def view_edit_subjects(
        request: Request,
        db: Session = Depends(get_db),
):
    """
    GET /view/edit/subjects
    Zobrazí formulář pro editaci předmětů.
    """
    # Načti všechny předměty
    predmety_raw = PredmetService.get_all_predmety(db)

    # Načti všechny potřebné reference
    teachers = PredmetService.get_all_teachers(db)
    tridy = db.execute(select(Trida).order_by(Trida.nazev)).scalars().all()
    ucebny = db.execute(select(Ucebna).order_by(Ucebna.nazev)).scalars().all()
    hodiny = db.execute(select(VyucovaciHodina).order_by(VyucovaciHodina.id)).scalars().all()

    # Vytvoř seznam s extra daty
    predmety = []
    for p in predmety_raw:
        teacher = db.execute(
            select(Ucitel).where(Ucitel.id == p.id_ucitele)
        ).scalar_one_or_none()

        trida = db.execute(
            select(Trida).where(Trida.id == p.id_tridy)
        ).scalar_one_or_none()

        ucebna = db.execute(
            select(Ucebna).where(Ucebna.id == p.id_ucebny)
        ).scalar_one_or_none() if p.id_ucebny else None

        hodina = db.execute(
            select(VyucovaciHodina).where(VyucovaciHodina.id == p.id_hodiny)
        ).scalar_one_or_none() if p.id_hodiny else None

        predmety.append({
            "id": p.id,
            "nazev": p.nazev,
            "zamereni": p.zamereni.name if p.zamereni else "vseobecny",
            "puleny": p.puleny,
            "pocet_hodin": p.pocet_hodin,
            "trida_nazev": trida.nazev if trida else "?",
            "id_tridy": p.id_tridy,
            "ucitel_prijmeni": teacher.prijmeni if teacher else "?",
            "id_ucitele": p.id_ucitele,
            "ucebna_nazev": ucebna.nazev if ucebna else "–",
            "id_ucebny": p.id_ucebny,
            "hodina_nazev": hodina.nazev if hodina else "–",
            "id_hodiny": p.id_hodiny,
        })

    return templates.TemplateResponse(
        request=request,
        name="edit_subjects.html",
        context={
            "predmety": predmety,
            "teachers": teachers,
            "tridy": tridy,
            "ucebny": ucebny,
            "hodiny": hodiny,
        },
    )


@router.post("/subjects/change-teacher")
async def post_change_subjects(
        request: Request,
        db: Session = Depends(get_db),
):
    """
    POST /subjects/change-teacher
    Zpracuje změnu všech polí u předmětů.
    Form data:
      - teacher_<id>=<new_teacher_id>
      - trida_<id>=<new_trida_id>
      - ucebna_<id>=<new_ucebna_id>
      - hodina_<id>=<new_hodina_id>
      - pocet_hodin_<id>=<pocet>
      - puleny_<id>=on (checkbox)
      - zamereni_<id>=<enum_value>
    """
    # Načti form data
    form = await request.form()

    changes_made = 0

    # Procházej všechny položky ve formuláři
    for key, value in form.items():
        try:
            # Učitel
            if key.startswith("teacher_"):
                predmet_id = int(key.split("_")[1])
                new_teacher_id = int(value) if value else None

                if new_teacher_id is not None and new_teacher_id > 0:
                    PredmetService.change_field(db, predmet_id, "id_ucitele", new_teacher_id)
                    changes_made += 1

            # Třída
            elif key.startswith("trida_"):
                predmet_id = int(key.split("_")[1])
                new_trida_id = int(value) if value else None

                if new_trida_id is not None and new_trida_id > 0:
                    PredmetService.change_field(db, predmet_id, "id_tridy", new_trida_id)
                    changes_made += 1

            # Učebna
            elif key.startswith("ucebna_"):
                predmet_id = int(key.split("_")[1])
                new_ucebna_id = int(value) if value else None

                if new_ucebna_id is not None and new_ucebna_id > 0:
                    PredmetService.change_field(db, predmet_id, "id_ucebny", new_ucebna_id)
                    changes_made += 1

            # Hodina
            elif key.startswith("hodina_"):
                predmet_id = int(key.split("_")[1])
                new_hodina_id = int(value) if value else None

                if new_hodina_id is not None and new_hodina_id > 0:
                    PredmetService.change_field(db, predmet_id, "id_hodiny", new_hodina_id)
                    changes_made += 1

            # Počet hodin
            elif key.startswith("pocet_hodin_"):
                predmet_id = int(key.split("_")[2])
                pocet = int(value) if value else None

                if pocet is not None and pocet > 0:
                    PredmetService.change_field(db, predmet_id, "pocet_hodin", pocet)
                    changes_made += 1

            # Půlený (checkbox)
            elif key.startswith("puleny_"):
                predmet_id = int(key.split("_")[1])
                is_puleny = value == "on"
                PredmetService.change_field(db, predmet_id, "puleny", is_puleny)
                changes_made += 1

            # Zaměření
            elif key.startswith("zamereni_"):
                predmet_id = int(key.split("_")[1])
                if value:
                    PredmetService.change_field(db, predmet_id, "zamereni", value)
                    changes_made += 1

        except (ValueError, IndexError):
            continue

    # Redirect zpět na formulář
    if changes_made > 0:
        return RedirectResponse(
            url=f"/view/edit/subjects?message=Změněno%20{changes_made}%20položek.",
            status_code=303
        )
    else:
        return RedirectResponse(
            url="/view/edit/subjects",
            status_code=303
        )