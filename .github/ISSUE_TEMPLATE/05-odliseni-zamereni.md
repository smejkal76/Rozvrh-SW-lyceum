---
name: "05 – Odlišení dle zaměření tříd"
about: "UI/Service • medium"
title: "[05] Odlišení dle zaměření tříd"
labels: "area:ui, area:service, level:medium, type:feature"
assignees: ""
---

**Cíl**
Odlišit třídy podle zaměření (např. humanitní / přírodovědné) v tabulce.

**Přesné zadání (scope)**
- Buď seskupit třídy do bloků s nadpisem, nebo barevně odlišit řádky.
- Použít existující data (bez změny schématu DB).

**Orientační postup**
1) Dostat zaměření třídy do výstupních dat (SQL/ORM).
2) Rozšířit view-model (např. `trida -> zamereni`).
3) V šabloně přidat CSS class podle zaměření.
4) Přidat legendu (box s vysvětlením barev).

**Soubory (doporučení)**
- `app/services/rozvrh_service.py`
- `app/web/timetable.py`
- `app/templates/day.html`
- `app/static/style.css`

**Definition of Done**
- [ ] Zaměření je vidět a konzistentní
- [ ] Legenda vysvětluje barvy
- [ ] Screenshot v PR
