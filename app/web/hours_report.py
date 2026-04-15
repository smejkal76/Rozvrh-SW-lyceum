from __future__ import annotations
import csv
import io
from typing import Generator
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.hours_report_service import fetch_hours_summary, build_pivot
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/view/reports/hours-summary", response_class=HTMLResponse)
def view_hours_summary(request: Request, db: Session = Depends(get_db)):
    rows = fetch_hours_summary(db)
    pivot = build_pivot(rows)
    return templates.TemplateResponse("hours_summary.html", {"request": request, "tridy": pivot.tridy, "zamereni": pivot.zamereni, "data": pivot.data, "radky_soucet": pivot.radky_soucet, "sloupce_soucet": pivot.sloupce_soucet, "celkem": pivot.celkem})
@router.get("/view/reports/hours-summary/export")
def export_hours_csv(db: Session = Depends(get_db)):
    rows = fetch_hours_summary(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["trida", "zamereni", "celkem_hodin"])
    for r in rows:
        writer.writerow([r.trida, r.zamereni, r.celkem_hodin])
    csv_data = "\ufeff" + output.getvalue()
    return StreamingResponse(io.StringIO(csv_data), media_type="text/csv; charset=utf-8-sig", headers={"Content-Disposition": "attachment; filename=hodiny_report.csv"})
