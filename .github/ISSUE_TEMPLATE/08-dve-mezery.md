---
name: "08 – Rozvrh bez dvou mezer denně"
about: "Service/Algoritmus • hard"
title: "[08] Rozvrh bez dvou mezer denně"
labels: "area:service, level:hard, type:feature"
assignees: ""
---

**Cíl**
Zakázat, aby jedna třída měla v jednom dni 2+ mezer mezi hodinami.

**Přesné zadání (scope)**
- Mezera = prázdná hodina mezi dvěma vyučovanými hodinami v rámci dne.
- Doporučeno: detekce + regenerace (max N pokusů).

**Orientační postup**
1) Implementuj `count_gaps_for_class_day(...)`.
2) Po generování zkontroluj všechny třídy a dny.
3) Při porušení opakuj generování, loguj důvod.
4) Přidej metriku do generation logu (Issue #07).

**Definition of Done**
- [ ] Pravidlo je vynucené
- [ ] V logu je vidět, zda bylo porušeno
- [ ] Existuje test/ověření na datech
