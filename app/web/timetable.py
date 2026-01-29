from __future__ import annotations

import inspect
from typing import Any, Dict, Generator

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.rozvrh_service import build_day_matrix, fetch_hodiny

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DNY = ["Po", "Ut", "St", "Ct", "Pa"]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _build_matrix_compat(*, den: str, hodiny: Any):
    """Compat wrapper pro různé signatury build_day_matrix.

    V tomto projektu je build_day_matrix ve skutečnosti definováno jako:
      build_day_matrix(hodiny: List[HodinaView], den: str, all_hours: List[int])

    Předchozí kompatibilní wrapper chybně posílal do all_hours samotné `hodiny`,
    čímž se do matrix.hodiny dostaly objekty HodinaView a následně padalo
    indexování cells přes (trida, h).

    Tohle řešení:
      - vždy pošle `hodiny` jen do parametru `hodiny` (pokud existuje)
      - do `all_hours` pošle pevný seznam [1..7] (nebo si ho odvoď níže, když budeš chtít)
    """

    sig = inspect.signature(build_day_matrix)
    params = sig.parameters

    kwargs: Dict[str, Any] = {}

    # den/day
    if "den" in params:
        kwargs["den"] = den
    elif "day" in params:
        kwargs["day"] = den

    # hodiny
    if "hodiny" in params:
        kwargs["hodiny"] = hodiny

    # all_hours: v tvé implementaci je to List[int] (1–7)
    if "all_hours" in params:
        kwargs["all_hours"] = [1, 2, 3, 4, 5, 6, 7]

    # 1) keyword call (preferované)
    if kwargs:
        return build_day_matrix(**kwargs)

    # 2) fallbacky (kdyby se signatura někdy změnila)
    names = list(params.keys())
    if len(names) >= 3 and names[2] == "all_hours":
        return build_day_matrix(hodiny, den, [1, 2, 3, 4, 5, 6, 7])
    if len(names) >= 2:
        first = names[0].lower()
        if first in {"den", "day"}:
            return build_day_matrix(den, hodiny)
        return build_day_matrix(hodiny, den)

    return build_day_matrix(hodiny)


@router.get("/api/day")
def api_day(
    den: str = Query("Po", pattern="^(Po|Ut|St|Ct|Pa)$"),
    db: Session = Depends(get_db),
):
    hodiny = fetch_hodiny(db, den=den)
    matrix = _build_matrix_compat(den=den, hodiny=hodiny)

    # JSON struktura vhodná pro budoucí JS frontend
    data: Dict[str, Dict[str, str]] = {}
    for trida in getattr(matrix, "tridy", []):
        data[trida] = {}
        for h in getattr(matrix, "hodiny", []):
            cell = matrix.cells.get((trida, h), "")
            data[trida][str(h)] = cell

    return JSONResponse(
        {
            "den": getattr(matrix, "den", den),
            "tridy": getattr(matrix, "tridy", []),
            "hodiny": getattr(matrix, "hodiny", []),
            "cells": data,
        }
    )


@router.get("/view/day", response_class=HTMLResponse)
def view_day(
    request: Request,
    den: str = Query("Po", pattern="^(Po|Ut|St|Ct|Pa)$"),
    db: Session = Depends(get_db),
):
    hodiny = fetch_hodiny(db, den=den)
    matrix = _build_matrix_compat(den=den, hodiny=hodiny)

    rows = []
    for trida in getattr(matrix, "tridy", []):
        rows.append(
            {
                "trida": trida,
                "cells": [matrix.cells.get((trida, h), "") for h in getattr(matrix, "hodiny", [])],
            }
        )

    return templates.TemplateResponse(
        "day.html",                         # konkrétní šablona, do které se budou vkládat data
        {
            "request": request,
            "den": den,
            "dny": DNY,
            "hodiny": getattr(matrix, "hodiny", []),
            "rows": rows,
        },
    )
