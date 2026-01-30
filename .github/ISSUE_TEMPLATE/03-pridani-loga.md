---
name: "03 – Přidání loga aplikace"
about: "UI • easy"
title: "[03] Přidání loga aplikace"
labels: "area:ui, level:easy, type:feature"
assignees: ""
---

**Cíl**
Přidat logo do hlavičky webu.

**Přesné zadání (scope)**
- Uložit logo do `app/static/` (SVG/PNG).
- Zobrazit v hlavičce na všech stránkách (zatím alespoň `day.html`).
- Logo nesmí rozbít mobilní layout.

**Orientační postup**
1) Přidej soubor `logo.svg`/`logo.png` do `app/static/`.
2) Uprav `day.html`: vlož `<img src="/static/logo.svg" ...>`.
3) Dolaď CSS (max-height, margin, align).
4) Otestuj desktop + mobile.

**Soubory (doporučení)**
- `app/templates/day.html`
- `app/static/style.css`
- `app/static/logo.svg` (nový soubor)

**Definition of Done**
- [ ] Logo je vidět a nepadá layout
- [ ] Funguje i na mobilu
- [ ] Screenshot v PR
