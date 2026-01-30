---
name: "18 – Kontrolní výpis úvazků učitelů"
about: "Reports/Service • medium"
title: "[18] Kontrolní výpis úvazků učitelů"
labels: "area:service, level:medium, type:feature"
assignees: ""
---

**Cíl**
Report: učitel → počet hodin týdně.

**Přesné zadání (scope)**
- Jen read-only HTML report.
- Volitelně řazení podle počtu hodin.

**Orientační postup**
1) SQL agregace: sum(pocet_hodin) group by učitel.
2) View `/view/reports/teacher-load`.
3) Šablona tabulky, řazení (volitelně).
4) Ověřit na datech.

**Definition of Done**
- [ ] Report je dostupný v UI
- [ ] Výsledky dávají smysl
- [ ] (Volitelně) řazení funguje
