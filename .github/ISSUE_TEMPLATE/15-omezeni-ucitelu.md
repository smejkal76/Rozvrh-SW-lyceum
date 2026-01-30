---
name: "15 – Časové omezení učitelů"
about: "Web/DB/Constraints • hard"
title: "[15] Časové omezení učitelů"
labels: "area:web, area:db, level:hard, type:feature"
assignees: ""
---

**Cíl**
CRUD časových omezení učitelů.

**Přesné zadání (scope)**
- Implementovat Create + Read + Delete.
- Update není nutné (řeš delete+create).
- Základní validace: existence učitele; volitelně kontrola překryvů.

**Orientační postup**
1) View `/view/constraints/teachers` s filtrem na učitele.
2) Form add (den, hodina_od, délka) + list omezení.
3) Endpointy add/delete.
4) Generátor respektuje omezení.

**Definition of Done**
- [ ] Omezení lze přidat a smazat
- [ ] Omezení se ukládají do DB
- [ ] Generátor omezení respektuje
