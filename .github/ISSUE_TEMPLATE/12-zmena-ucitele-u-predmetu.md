---
name: "12 – Editace předmětů – změna učitele"
about: "Web/DB • medium"
title: "[12] Editace předmětů – změna učitele"
labels: "area:web, area:db, level:medium, type:feature"
assignees: ""
---

**Cíl**
Umožnit změnit učitele u předmětu (UPDATE).

**Přesné zadání (scope)**
- Implementovat pouze: Read seznam předmětů + Update učitele.
- Neimplementovat create/delete předmětů.

**Orientační postup**
1) View `/view/edit/subjects`: tabulka předmětů + select učitele.
2) POST `/subjects/{id}/change-teacher`.
3) Validace: učitel existuje.
4) Redirect zpět.

**Definition of Done**
- [ ] Změna se uloží do DB
- [ ] Je ošetřeno, že učitel existuje
- [ ] UI je použitelné
