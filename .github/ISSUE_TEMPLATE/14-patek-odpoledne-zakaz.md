---
name: "14 – Časové omezení rozvrhu – zákaz odpoledních hodin v pátek"
about: "Service/Constraints • medium"
title: "[14] Časové omezení rozvrhu – zákaz odpoledních hodin v pátek"
labels: "area:service, level:medium, type:feature"
assignees: ""
---

**Cíl**
Zakázat výuku v pátek odpoledne (např. hodina_od >= 6).

**Přesné zadání (scope)**
- Vynutit v generátoru (constraint).
- V UI to zobrazit jako omezení (navázat na Issue #04).

**Orientační postup**
1) Definuj hranici „odpoledne“ (konstanta).
2) V generátoru zakaž sloty (Pa, 6–7).
3) Zapiš do logu generování/validace.
4) V UI zvýrazni zakázané sloty.

**Definition of Done**
- [ ] Pátek odpoledne je bez výuky
- [ ] Pravidlo je zdokumentované
- [ ] V UI je vidět omezení
