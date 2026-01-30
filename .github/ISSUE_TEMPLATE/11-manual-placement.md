---
name: "11 – Ruční umístění vybraných hodin"
about: "Web/Service • hard"
title: "[11] Ruční umístění vybraných hodin"
labels: "area:web, area:service, level:hard, type:feature"
assignees: ""
---

**Cíl**
Umožnit ručně fixovat hodinu na den + hodina_od.

**Přesné zadání (scope)**
- UI: formulář (předmět, den, hodina_od) + seznam fixací + delete.
- Uložit do DB.
- Generátor musí fixace respektovat.

**Orientační postup**
1) DB tabulka `manual_placement` (predmet_id, den, hodina_od).
2) View `/view/manual/placements`.
3) Endpointy add/delete.
4) Generátor načítá fixy a blokuje sloty.

**Definition of Done**
- [ ] Fixace se uloží a jde smazat
- [ ] Generátor fixace respektuje
- [ ] Změna je vidět po regeneraci
