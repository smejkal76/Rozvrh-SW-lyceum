from __future__ import annotations

import argparse
from typing import Dict, List

from app.database import SessionLocal
from app.services.rozvrh_service import fetch_hodiny, build_day_matrix, DayMatrix

DENNI_HODINY = [1, 2, 3, 4, 5, 6, 7]

DEN_MAP: Dict[str, str] = {
    "1": "Po",
    "po": "Po",
    "po.": "Po",

    "2": "Ut",
    "ut": "Ut",
    "út": "Ut",
    "ut.": "Ut",

    "3": "St",
    "st": "St",
    "st.": "St",

    "4": "Ct",
    "ct": "Ct",
    "čt": "Ct",
    "ct.": "Ct",

    "5": "Pa",
    "pa": "Pa",
    "pá": "Pa",
    "pa.": "Pa",
}

DNY_TYDNE: List[str] = ["Po", "Ut", "St", "Ct", "Pa"]


# ---------- Pomocné funkce ----------

def _normalize_day(value: str) -> str:
    key = value.strip().lower()
    if key not in DEN_MAP:
        raise ValueError(f"Neplatný den: {value!r}. Použij Po/Ut/St/Ct/Pa nebo 1–5.")
    return DEN_MAP[key]


def _format_cell(text: str, width: int) -> str:
    text = (text or "").replace("\n", " / ")
    if len(text) > width:
        text = text[: width - 1] + "…"
    return text.ljust(width)


def _print_day_matrix(matrix: DayMatrix) -> None:
    if not matrix.tridy:
        print(f"Pro den {matrix.den} není v rozvrhu žádná hodina.")
        return

    class_col_width = max(len("třída"), max(len(t) for t in matrix.tridy))

    col_widths = {}
    for h in matrix.hodiny:
        obsah = [matrix.cells.get((t, h), "") for t in matrix.tridy]
        max_len = max([len(str(h))] + [len(c.replace("\n", " / ")) for c in obsah])
        col_widths[h] = max_len

    header = _format_cell("třída", class_col_width) + " | " + " | ".join(
        _format_cell(str(h), col_widths[h]) for h in matrix.hodiny
    )
    print(header)
    print("-" * len(header))

    for trida in matrix.tridy:
        row_parts = [_format_cell(trida, class_col_width)]
        for h in matrix.hodiny:
            obsah = matrix.cells.get((trida, h), "")
            row_parts.append(_format_cell(obsah, col_widths[h]))
        print(" | ".join(row_parts))


def _filter_matrix_for_class(matrix: DayMatrix, trida: str) -> DayMatrix:
    """Vrátí matici jen pro jednu třídu."""
    if trida not in matrix.tridy:
        return DayMatrix(den=matrix.den, tridy=[], hodiny=matrix.hodiny, cells={})

    cells = {
        (t, h): v
        for (t, h), v in matrix.cells.items()
        if t == trida
    }
    return DayMatrix(den=matrix.den, tridy=[trida], hodiny=matrix.hodiny, cells=cells)


# ---------- Příkazy CLI ----------

def cmd_show_day(args: argparse.Namespace) -> None:
    den = _normalize_day(args.den)

    with SessionLocal() as session:
        hodiny = fetch_hodiny(session, den=den)

    matrix = build_day_matrix(hodiny, den=den, all_hours=DENNI_HODINY)

    print(f"Rozvrh pro den {den}:")
    _print_day_matrix(matrix)


def cmd_show_week(args: argparse.Namespace) -> None:
    with SessionLocal() as session:
        hodiny = fetch_hodiny(session)

    for den in DNY_TYDNE:
        matrix = build_day_matrix(hodiny, den=den, all_hours=DENNI_HODINY)
        print()
        print(f"=== {den} ===")
        _print_day_matrix(matrix)


def cmd_show_week_class(args: argparse.Namespace) -> None:
    trida = args.trida

    with SessionLocal() as session:
        hodiny = fetch_hodiny(session)

    dostupne_tridy = sorted({h.trida for h in hodiny})
    if trida not in dostupne_tridy:
        print(f"Třída {trida!r} v rozvrhu neexistuje.")
        print("Dostupné třídy:")
        for t in dostupne_tridy:
            print(f"  - {t}")
        return

    for den in DNY_TYDNE:
        matrix = build_day_matrix(hodiny, den=den, all_hours=DENNI_HODINY)
        matrix_trida = _filter_matrix_for_class(matrix, trida)

        print()
        print(f"=== {den} – třída {trida} ===")
        if not matrix_trida.tridy:
            print("Žádné hodiny.")
        else:
            _print_day_matrix(matrix_trida)


# ---------- main ----------

def main() -> None:
    parser = argparse.ArgumentParser(prog="rozvrh-cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # show-day
    p_show = subparsers.add_parser("show-day", help="Zobrazí rozvrh pro jeden den")
    p_show.add_argument(
        "--den",
        "-d",
        required=True,
        help="Den v týdnu (Po/Ut/St/Ct/Pa nebo 1–5).",
    )
    p_show.set_defaults(func=cmd_show_day)

    # show-week
    p_week = subparsers.add_parser(
        "show-week", help="Zobrazí rozvrh pro celý týden (Po–Pa)"
    )
    p_week.set_defaults(func=cmd_show_week)

    # show-week-class
    p_week_class = subparsers.add_parser(
        "show-week-class",
        help="Zobrazí rozvrh pro celý týden (Po–Pa) pro vybranou třídu",
    )
    p_week_class.add_argument(
        "--trida",
        "-t",
        required=True,
        help="Název třídy přesně podle rozvrhu (např. '10. Lyceum').",
    )
    p_week_class.set_defaults(func=cmd_show_week_class)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    # Přímé spuštění bez argumentů → automaticky show-day --den Po
    import sys

    if len(sys.argv) == 1:
        #sys.argv.extend(["show-day", "--den", "Po"])
        sys.argv.extend(["show-week"])
        #sys.argv.extend(["show-week-class", "--trida", "10 L"])

    main()
