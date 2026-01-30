---
name: "01 – Design webové aplikace"
about: "UI • easy"
title: "[01] Design webové aplikace"
labels: "area:ui, level:easy, type:feature"
assignees: ""
---

**Cíl**
Zavést základní vizuální styl aplikace (barvy, fonty, zarovnání, tabulky). Bez změn DB a business logiky.

**Přesné zadání (scope)**
- Měnit pouze HTML/CSS.
- Upravit: hlavičku, ovládací prvky (select), tabulku, prázdný stav, patičku.
- Nepřidávat logo (to je samostatné Issue #03).

**Orientační postup**
1) Projdi `app/templates/day.html` a identifikuj hlavní bloky.
2) V `app/static/style.css` zaveď CSS proměnné pro barvy a typografii.
3) Vylepši tabulku: zebra řádků, hover, lepší padding (stickies zachovat).
4) Otestuj v prohlížeči, přidej screenshot do PR.

**Soubory (doporučení)**
- `app/templates/day.html`
- `app/static/style.css`

**Definition of Done**
- [ ] Vzhled je konzistentní a čitelný
- [ ] Bez změn backend logiky
- [ ] Screenshot v PR
- [ ] PR popis: co AI navrhla a co bylo upraveno ručně

**Testování (doplň)**
- Kroky, jak ověřit změny v prohlížeči
