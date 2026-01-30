---
name: "20 – Mobilní aplikace (Android / iOS) – prototyp"
about: "Mobile • hard"
title: "[20] Mobilní aplikace – prototyp"
labels: "area:mobile, level:hard, type:feature"
assignees: ""
---

**Cíl**
Vytvořit prototyp mobilní aplikace, která čte rozvrh z JSON API.

**Přesné zadání (scope)**
- Read-only: načíst `/api/day?den=Po` a zobrazit.
- Přepínání dne (Po–Pa).
- Není nutný login ani editace.

**Orientační postup**
1) Vybrat technologii (Flutter / React Native / native).
2) Implementovat volání API a parsování JSON.
3) Zobrazit data (list nebo jednoduchá tabulka).
4) Přidat přepínač dne.

**Definition of Done**
- [ ] Prototyp umí načíst a zobrazit rozvrh
- [ ] Přepínání dne funguje
- [ ] Krátký README (jak spustit)
