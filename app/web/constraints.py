from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import constraints_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- DB dependency (stejný vzor jako timetable.py) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- READ: zobrazení stránky se seznamem a formulářem ---
@router.get("/view/constraints", response_class=HTMLResponse)
def view_constraints(request: Request, db: Session = Depends(get_db)):
    omezeni = constraints_service.get_all_omezeni_rozvrhu(db)
    dny = ['Po', 'Ut', 'St', 'Ct', 'Pa']
    return templates.TemplateResponse("constraints_timetable.html", {
        "request": request,
        "omezeni": omezeni,
        "dny": dny,
        "hodiny": range(1, 8)
    })

# --- CREATE: zpracování formuláře ---
@router.post("/view/constraints/add")
def add_constraint(
    nazev: str = Form(...),
    den: str = Form(...),
    hodina_od: int = Form(...),
    delka: int = Form(...),
    db: Session = Depends(get_db)
):
    constraints_service.add_omezeni_rozvrhu(db, nazev, den, hodina_od, delka)
    return RedirectResponse(url="/view/constraints", status_code=303)

# --- DELETE: smazání záznamu ---
@router.post("/view/constraints/delete/{omezeni_id}")
def delete_constraint(omezeni_id: int, db: Session = Depends(get_db)):
    constraints_service.delete_omezeni_rozvrhu(db, omezeni_id)
    return RedirectResponse(url="/view/constraints", status_code=303)