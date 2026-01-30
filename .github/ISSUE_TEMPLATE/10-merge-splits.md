---
name: "10 – Ruční spojování půlených předmětů"
about: "Web/Service • hard"
title: "[10] Ruční spojování půlených předmětů"
labels: "area:web, area:service, level:hard, type:feature"
assignees: ""
---

**Cíl**
Umožnit ručně „spojit“ půlené předměty (běží ve stejný čas).

**Přesné zadání (scope)**
- UI: stránka „Půlené předměty“ + akce spojit/rozpojit.
- Bez drag&drop.
- Uložit do DB (flag nebo merge_group_id).

**Orientační postup**
1) Přidej do DB strukturu pro manual merge.
2) Přidej view `/view/manual/merge-splits`.
3) Endpointy merge/unmerge (POST).
4) Generátor při dalším běhu respektuje manual merge.

**Definition of Done**
- [ ] Lze spojit/rozpojit
- [ ] Stav se uloží do DB
- [ ] Generátor to respektuje
