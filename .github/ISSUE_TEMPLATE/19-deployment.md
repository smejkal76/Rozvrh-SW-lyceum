---
name: "19 – Deployment na webový server"
about: "Infra/Release • medium"
title: "[19] Deployment na webový server"
labels: "area:infra, level:medium, type:release"
assignees: ""
---

**Cíl**
Nasadit aplikaci na veřejný server s automatickým deploy po merge do `main`.

**Přesné zadání (scope)**
- Render nebo Railway (vyber jednu platformu).
- Nastavit env vars (DATABASE_URL apod.).
- Start command přes uvicorn.

**Orientační postup**
1) Připojit GitHub repo na platformě.
2) Nastavit build + start příkaz.
3) Zřídit DB (managed Postgres) a nastavit `DATABASE_URL`.
4) Ověřit veřejnou URL a přidat do README.

**Definition of Done**
- [ ] Aplikace je veřejně dostupná na URL
- [ ] Deploy probíhá automaticky z `main`
- [ ] README obsahuje odkaz a popis env vars
