---
name: "04 – Zobrazení / skrytí časových omezení"
about: "Web/UI • medium"
title: "[04] Zobrazení / skrytí časových omezení"
labels: "area:web, area:ui, level:medium, type:feature"
assignees: ""
---

**Cíl**
Přidat přepínač „Zobrazit omezení“ a vizuálně označit zakázané sloty.

**Přesné zadání (scope)**
- V1 stačí vizuální zvýraznění (šrafování/ztlumení) zakázaných slotů v tabulce.
- Ovládání přes query parametr (např. `?show_limits=1`) nebo checkbox s auto-submit.
- Pokud zatím nejsou data omezení napojená, použij demo: pátek 6–7.

**Orientační postup**
1) Přidej do `/view/day` parametr `show_limits` a předej do šablony.
2) V `timetable.py` připrav `disabled_slots={(den, hodina)}`.
3) V `day.html` přidej class pro zakázané buňky.
4) V `style.css` udělej šrafování/ztlumení.

**Soubory (doporučení)**
- `app/web/timetable.py`
- `app/templates/day.html`
- `app/static/style.css`

**Definition of Done**
- [ ] Přepínač funguje
- [ ] Zakázané sloty jsou jasně vidět
- [ ] Bez chyb v konzoli/logu
- [ ] Screenshot v PR
