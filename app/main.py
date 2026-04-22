from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.web.timetable import router as timetable_router
from app.web.subjects import router as subjects_router
from app.web.teachers import router as teachers_router
from app.web.hours_report import router as hours_report_router

app = FastAPI(title="Rozvrh SŠ")

app.include_router(timetable_router)
app.include_router(subjects_router)
app.include_router(teachers_router)
app.include_router(hours_report_router)

# statické soubory (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {"ok": True, "open": "/view/day?den=Po"}
