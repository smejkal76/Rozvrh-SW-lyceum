from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.omezeni_service import (
    list_teacher_constraints,
    create_teacher_constraint,
    delete_teacher_constraint
)
from app.services.ucitel_service import list_ucitele
from app.templates import templates

router = APIRouter()


def load_teacher_constraints(session, busy_ucitel, H): ...
def load_room_constraints(session, busy_ucebna, H): ...
def load_global_constraints(session, block_rozvrh, H): ...



from collections import defaultdict

def init_calendars(H):
    return {
        "busy_ucitel": defaultdict(lambda: [False] * (H + 1)),
        "busy_ucebna": defaultdict(lambda: [False] * (H + 1)),
        "busy_trida": defaultdict(lambda: [False] * (H + 1)),
        "block_rozvrh": defaultdict(lambda: [False] * (H + 1)),
    }


def load_teacher_constraints(session, busy_ucitel, H):
    rows = session.execute("""
        SELECT id_ucitele, den, hodina_od, delka
        FROM casove_omezeni_ucitele
    """).fetchall()

    for r in rows:
        for h in range(r.hodina_od, r.hodina_od + r.delka):
            busy_ucitel[(r.id_ucitele, r.den)][h] = True


def is_teacher_free(busy_ucitel, ucitel, den, start, L):
    for h in range(start, start + L):
        if busy_ucitel[(ucitel, den)][h]:
            return False
    return True