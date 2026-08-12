# 5 — CI/CD (GitHub Actions)

## Kontekst

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 11. Minimalny sensowny zakres dla
tego projektu: testy na PR/push + build obrazu + deploy.

## Kroki (szkic — do rozwinięcia bliżej realizacji)

- [ ] `.github/workflows/run_test.yml` — `uv sync` + `make run_test` na
      branchach innych niż `main`, z serwisem `postgres` w GitHub Actions
- [ ] `.github/workflows/run_production.yml` — build + push obrazu na `main`
- [ ] Deploy step — zależny od decyzji w [4 — infra](4-infra.md)

## Status

- [ ] Zablokowane do czasu ukończenia pkt. 2 (tooling) i pkt. 4 (infra)
