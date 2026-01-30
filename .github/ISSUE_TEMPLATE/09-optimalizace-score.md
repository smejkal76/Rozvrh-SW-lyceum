---
name: "09 – Optimalizace vygenerovaného rozvrhu"
about: "Service/Algoritmus • hard"
title: "[09] Optimalizace vygenerovaného rozvrhu"
labels: "area:service, level:hard, type:feature"
assignees: ""
---

**Cíl**
Vybrat nejlepší rozvrh z N pokusů podle skóre.

**Přesné zadání (scope)**
- Definovat skóre (např. mezery, páteční odpoledne, nerovnoměrnost).
- Uložit nejlepší rozvrh do DB + uložit log pokusů.

**Orientační postup**
1) Napiš funkci `score(timetable)`.
2) Proveď N generací, drž nejlepší skóre.
3) Ulož nejlepší řešení, loguj attempt + score.
4) Zobraz skóre v UI (navázat na #07).

**Definition of Done**
- [ ] Skóre je definované a použité
- [ ] Ukládá se nejlepší řešení
- [ ] Log obsahuje pokusy a skóre
