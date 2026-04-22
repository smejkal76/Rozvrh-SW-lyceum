from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.services.ucitel_service import list_ucitele, create_ucitel, delete_ucitel
from app.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/view/edit/teachers")
def teachers_list(request: Request, db: Session = Depends(get_db)):
    ucitele = list_ucitele(db)
    error = request.query_params.get("error")

    return templates.TemplateResponse("teachers.html", {
        "request": request,
        "ucitele": ucitele,
        "error": error
    })


@router.get("/view/teachers/new")
def new_teacher_form(request: Request):
    return templates.TemplateResponse("teacher_form.html", {
        "request": request
    })


@router.post("/teachers")
def create_teacher(
    jmeno: str = Form(...),
    prijmeni: str = Form(...),
    db: Session = Depends(get_db)
):
    create_ucitel(db, jmeno, prijmeni)
    return RedirectResponse("/view/edit/teachers", status_code=303)


@router.post("/teachers/{id}/delete")
def delete_teacher(id: int, db: Session = Depends(get_db)):
    success = delete_ucitel(db, id)

    if not success:
        return RedirectResponse("/view/edit/teachers?error=has_relations", status_code=303)

    return RedirectResponse("/view/edit/teachers", status_code=303)