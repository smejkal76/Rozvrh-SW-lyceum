# seznam
GET  /view/teachers

# formuláře
GET  /view/teachers/new
GET  /view/teachers/{id}/edit

# akce
POST /teachers
POST /teachers/{id}
POST /teachers/{id}/delete

from app.services.omezeni_ucitele_service import *

@router.get("/view/teachers/{id}/constraints", response_class=HTMLResponse)
def teacher_constraints(request: Request, id: int, db=Depends(get_db)):
    ucitel = get_ucitel(db, id)
    omezeni = db.query(CasoveOmezeniUcitel).filter(
        CasoveOmezeniUcitel.id_ucitele == id
    ).all()

    return templates.TemplateResponse("teacher_constraints.html", {
        "request": request,
        "ucitel": ucitel,
        "omezeni": omezeni
    })

@router.get("/view/teachers/{id}/constraints/new", response_class=HTMLResponse)
def new_constraint(request: Request, id: int):
    return templates.TemplateResponse("constraint_form.html", {
        "request": request,
        "id_ucitele": id
    })

@router.post("/teachers/{id}/constraints")
def create_constraint(
    id: int,
    den: str = Form(...),
    hodina_od: int = Form(...),
    delka: int = Form(...),
    db=Depends(get_db)
):
    create_omezeni_ucitele(db, id, den, hodina_od, delka)
    return RedirectResponse(f"/view/teachers/{id}/constraints", status_code=303)

@router.post("/constraints/{cid}/delete")
def delete_constraint(cid: int, db=Depends(get_db)):
    obj = get_omezeni_ucitele(db, cid)
    teacher_id = obj.id_ucitele

    delete_omezeni_ucitele(db, cid)

    return RedirectResponse(f"/view/teachers/{teacher_id}/constraints", status_code=303)