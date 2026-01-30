---
name: "16 – Časové omezení učeben"
about: "Web/DB/Constraints • hard"
title: "[16] Časové omezení učeben"
labels: "area:web, area:db, level:hard, type:feature"
assignees: ""
---

**Cíl**
CRUD časových omezení učeben.

**Přesné zadání (scope)**
- Implementovat Create + Read + Delete.
- Update není nutné.
- Validace: existence učebny; volitelně kontrola překryvů.

**Orientační postup**
1) View `/view/constraints/rooms`.
2) Form add + list + delete.
3) Endpointy add/delete.
4) Generátor respektuje omezení.

**Definition of Done**
- [ ] Omezení učeben fungují (add/delete)
- [ ] Ukládají se do DB
- [ ] Generátor omezení respektuje
