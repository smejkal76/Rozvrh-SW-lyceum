from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.web.timetable import router as timetable_router
from app.web.subjects import router as subjects_router  # ← PŘIDEJ TUTO ŘÁDKU

app = FastAPI(title="Rozvrh SŠ")

app.include_router(timetable_router)
app.include_router(subjects_router)  # ← PŘIDEJ TUTO ŘÁDKU

# statické soubory (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    return {"ok": True, "open": "/view/day?den=Po"}

from app.web import teachers

app.include_router(teachers.router)

from app.web.teachers import router as teachers_router

app.include_router(teachers_router)