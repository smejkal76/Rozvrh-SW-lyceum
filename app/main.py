from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.web.timetable import router as timetable_router

app = FastAPI(title="Rozvrh SŠ")

app.include_router(timetable_router)

# statické soubory (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    # jednoduchý redirect by šel taky, ale nechám to minimalisticky:
    return {"ok": True, "open": "/view/day?den=Po"}
