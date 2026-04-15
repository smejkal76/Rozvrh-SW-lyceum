from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.web.timetable import router as timetable_router
from app.web.hours_report import router as hours_router

app = FastAPI(title="Rozvrh SS")

app.include_router(timetable_router)
app.include_router(hours_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {"ok": True, "open": "/view/day?den=Po"}
