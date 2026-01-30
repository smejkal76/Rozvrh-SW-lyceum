---
name: "13 – Kontrolní výpis hodin v ročnících a zaměření"
about: "Reports/Service • medium"
title: "[13] Kontrolní výpis hodin v ročnících a zaměření"
labels: "area:service, level:medium, type:feature"
assignees: ""
---

**Cíl**
Report: součet hodin za týden podle ročníku/třídy a zaměření.

**Přesné zadání (scope)**
- Jen read-only report v HTML.
- Volitelně tlačítko „Export CSV“.

**Orientační postup**
1) V service vrstvě napsat agregační SQL dotaz.
2) View `/view/reports/hours-summary`.
3) Šablona tabulky, volitelně řazení.
4) Ověřit součty na datech.

**Definition of Done**
- [ ] Report se vykreslí a dává smysl
- [ ] Součty odpovídají datům
- [ ] (Volitelně) export CSV funguje
