---
name: "07 – Zobrazení průběhu generování"
about: "Web/Service/UI • hard"
title: "[07] Zobrazení průběhu generování"
labels: "area:web, area:service, area:ui, level:hard, type:feature"
assignees: ""
---

**Cíl**
Zobrazit průběh generování (iterace/opakování).

**Přesné zadání (scope)**
- V1 stačí zobrazit log po doběhu (ne realtime).
- Uživatel vidí: číslo pokusu, skóre/kolize, označení nejlepšího pokusu.

**Orientační postup**
1) Upravit generátor tak, aby vracel log pokusů.
2) Uložit log do DB (preferováno) nebo souboru.
3) Vytvořit view `/view/generation-log`.
4) Prolinkovat z `/view/generate`.

**Definition of Done**
- [ ] Log existuje a lze ho zobrazit
- [ ] Je jasné, který pokus vyhrál
- [ ] UI je čitelné
