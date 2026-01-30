---
name: "02 – Optimalizace pro mobilní zobrazení"
about: "UI • easy"
title: "[02] Optimalizace pro mobilní zobrazení"
labels: "area:ui, level:easy, type:feature"
assignees: ""
---

**Cíl**
Zajistit, že rozvrh je použitelný na telefonu (cca 390px).

**Přesné zadání (scope)**
- Bez změn backendu.
- Povolené řešení: horizontální scroll tabulky, sticky hlavička a první sloupec, menší font/padding.

**Orientační postup**
1) Obal tabulku do wrapperu s `overflow-x:auto` (pokud už není).
2) Přidej media queries do `style.css` (zmenšit padding, font-size).
3) Otestuj ve DevTools (device toolbar) + ideálně reálný mobil.

**Soubory (doporučení)**
- `app/static/style.css`
- `app/templates/day.html`

**Definition of Done**
- [ ] Na mobilu je stránka použitelná
- [ ] Tabulka se dá scrollovat / číst
- [ ] Screenshot mobilního náhledu v PR

**Testování (doplň)**
- DevTools → iPhone 12/SE a kontrola layoutu
