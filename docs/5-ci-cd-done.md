# 5 — CI/CD (GitHub Actions)

## Kontekst

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 11. Zakres dopasowany do decyzji z
[4 — infra](4-infra-done.md): pełny Ansible + Docker Swarm + Doppler, więc
CI/CD też pełne (test → build+push → deploy), nie okrojone.

## Zdecydowane już (przy okazji pkt. 4)

- GitHub Actions **environment `prod`** — sekrety deployu (`SSH_PRIVATE_KEY`,
  `ANSIBLE_PASSWORD`, `TARGET_HOST`, `SSH_USER`, `DOCKER_USERNAME`,
  `DOCKER_PASSWORD`, `REPOSITORY`) trzymane tam, nie jako zwykłe repo secrets

## Kroki (szkic — do rozwinięcia bliżej realizacji)

- [ ] `.github/workflows/run_test.yml` — `uv sync` + `make run_test` na
      branchach innych niż `main`, z serwisem `postgres` w GitHub Actions
- [ ] `.github/workflows/run_production.yml` — build (`infra/dockerfiles/production.dockerfile`)
      + push obrazu na `main`
- [ ] `.github/workflows/run_cd_production.yml` — deploy: `ansible-playbook
      infra/ansible/playbook_deploy.yml`, environment `prod`, renderuje
      `infra/ansible/inventory.ini` z sekretów `TARGET_HOST`/`SSH_USER`

## Status

- [ ] Zablokowane do czasu ukończenia pkt. 2 (tooling) i pkt. 4 (infra) — **oba
      ukończone**, ten task jest teraz odblokowany, ale świadomie odłożony
      (buduje się jak będzie chociaż jedna działająca sekcja z 3.1-3.5 do
      faktycznego wdrożenia)
