from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.ucebna_service import (
    list_ucebna, get_ucebna, create_ucebna, update_ucebna, delete_ucebna
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/view/classrooms", response_class=HTMLResponse)
def list_view(request: Request, db: Session = Depends(get_db)):
    ucebny = list_ucebna(db)
    return templates.TemplateResponse("classrooms.html", {
        "request": request,
        "ucebny": ucebny,
        "message": None
    })

@router.post("/classrooms")
def create(request: Request, nazev: str = Form(...), db: Session = Depends(get_db)):
    try:
        create_ucebna(db, nazev)
    except ValueError:
        pass
    return RedirectResponse("/view/classrooms", status_code=303)

@router.get("/view/classrooms/{id}/edit", response_class=HTMLResponse)
def edit_view(request: Request, id: int, db: Session = Depends(get_db)):
    ucebna = get_ucebna(db, id)
    return templates.TemplateResponse("classroom_form.html", {
        "request": request,
        "ucebna": ucebna
    })

@router.post("/classrooms/{id}")
def update(id: int, nazev: str = Form(...), db: Session = Depends(get_db)):
    try:
        update_ucebna(db, id, nazev)
    except ValueError:
        pass
    return RedirectResponse("/view/classrooms", status_code=303)

@router.post("/classrooms/{id}/delete")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        delete_ucebna(db, id)
    except ValueError:
        pass
    return RedirectResponse("/view/classrooms", status_code=303)