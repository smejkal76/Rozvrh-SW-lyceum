---
name: "06 – Nové generování rozvrhu na webu"
about: "Web/Service • hard"
title: "[06] Nové generování rozvrhu na webu"
labels: "area:web, area:service, level:hard, type:feature"
assignees: ""
---

**Cíl**
Tlačítko „Vygenerovat rozvrh“ spustí generátor a uloží výsledek do DB.

**Přesné zadání (scope)**
- Přidat POST endpoint (např. `/generate`).
- Po dokončení redirect zpět na rozvrh.
- V1 stačí blokující volání (bez async progress).

**Orientační postup**
1) Přidej endpoint `POST /generate` v routeru.
2) Zavolej service funkci, která generuje a ukládá do DB.
3) Ošetři chyby (hláška/HTTP 500).
4) V `day.html` přidej `<form method="post" action="/generate">`.

**Soubory (doporučení)**
- `app/web/timetable.py`
- generátor/service modul (dle projektu)
- `app/templates/day.html`

**Definition of Done**
- [ ] Kliknutí spustí generování a uloží data
- [ ] Po dokončení se zobrazí nový rozvrh
- [ ] Chyby jsou srozumitelně hlášené
