---
name: "17 – Učitelé – přidat / smazat"
about: "Web/DB • medium"
title: "[17] Učitelé – přidat / smazat"
labels: "area:web, area:db, level:medium, type:feature"
assignees: ""
---

**Cíl**
CRUD učitelů (základ).

**Přesné zadání (scope)**
- Implementovat Create + Read + Delete.
- Update není nutné.
- Delete: pokud jsou vazby (předměty), zobrazit hlášku a delete zakázat (nejjednodušší).

**Orientační postup**
1) View `/view/edit/teachers` (list + add form).
2) Endpoint create.
3) Endpoint delete s kontrolou vazeb.
4) Validace uniqueness (pokud dává smysl).

**Definition of Done**
- [ ] Lze přidat a smazat učitele (s validací vazeb)
- [ ] UI je použitelné
- [ ] Bez rozbití existujících dat
