# 5 — CI/CD (GitHub Actions)

## Kontekst

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 11, 1:1 przepisane z workflowów
projektu referencyjnego (`project-job-server-FastAPI`, katalog
`.github/workflows/`), dostosowane do decyzji z [4 — infra](4-infra-done.md):
pełny Ansible + Docker Swarm + Doppler, więc CI/CD też pełne
(test → container smoke → build+push → deploy), nie okrojone.

## Zdecydowane już (przy okazji pkt. 4)

- GitHub Actions **environment `prod`** — sekrety deployu (`SSH_PRIVATE_KEY`,
  `ANSIBLE_PASSWORD`, `TARGET_HOST`, `SSH_USER`, `DOCKER_USERNAME`,
  `DOCKER_PASSWORD`, `REPOSITORY`) trzymane tam, nie jako zwykłe repo secrets.
  `become_password` (hasło sudo, patrz pkt. 4) **nie** jest wśród nich — żyje
  tylko wewnątrz zaszyfrowanego `infra/ansible/secrets.yml`.

## Struktura

```
.github/workflows/
├── run_test_local.yml          ← trigger: push na branch != main
├── run_ci_test_local.yml       ← reusable: postgres:16 service + `make run_test`
├── run_production.yml          ← trigger: push na main / workflow_dispatch —
│                                   orkiestruje 3 poniższe joby po kolei
├── run_ci_test_containers.yml  ← reusable: `infra/scripts/ci/ci_smoke.sh`
├── run_ci_production.yml       ← reusable: build + push obrazu na Docker Hub
│                                   (tag = timestamp YYYYMMDDHHMM + `latest`)
└── run_cd_production.yml       ← reusable: ansible-playbook -> Docker Swarm

infra/scripts/ci/
└── ci_smoke.sh    ← 3-warstwowy smoke obrazu: build -> import -> boot + probe
```

## Kroki

- [x] `run_test_local.yml` + `run_ci_test_local.yml` — testy na branchach
      innych niż `main`; serwis `postgres:16` w GitHub Actions, zmienne
      `ARTURSCIBOR_BACKEND_*` wprost w `env:` joba (Settings czyta zmienne
      procesu priorytetowo, `env/*.env` nie jest tu potrzebny —
      `conftest.py` i tak sam tworzy `{DB_NAME}_test`); `make run_test`
- [x] `run_production.yml` — na `main`: `container_smoke` → `ci` → `cd` →
      `report` (podsumowanie + fail jeśli `cd` nie przeszedł). `environment: prod`
      ustawione na jobach `ci` i `cd` — bez tego reusable workflow nie
      dostałby sekretów przypisanych do tego środowiska
- [x] `run_ci_test_containers.yml` — wywołuje `infra/scripts/ci/ci_smoke.sh`
- [x] `run_ci_production.yml` — build (`infra/dockerfiles/production.dockerfile`)
      + push, nazwa obrazu z sekretu `REPOSITORY` (nie hardkodowana jak w
      projekcie referencyjnym — zgodnie z decyzją z pkt. 4 trzymania jej
      jako osobnego sekretu środowiska `prod`)
- [x] `run_cd_production.yml` — `ansible-playbook infra/ansible/playbook_deploy.yml`,
      renderuje `infra/ansible/inventory.ini` z sekretów `TARGET_HOST`/`SSH_USER`,
      odszyfrowuje `secrets.yml` przez `ANSIBLE_PASSWORD` — 1:1 z projektem
      referencyjnym, bez zmian (mechanizm nie zależy od konkretnego projektu)
- [x] `infra/scripts/ci/ci_smoke.sh` — wzorowany na projekcie referencyjnym,
      dostosowany: port **8000** (nie 3000), prefiks `ARTURSCIBOR_BACKEND_`,
      `infra/dockerfiles/production.dockerfile`, `uv run python -c` zamiast
      gołego `python` (ten obraz nie ma uv-venv na `PATH` poza `uv run`,
      w przeciwieństwie do obrazu referencyjnego), smoke probe na **`/docs`**
      zamiast `/health` — to API nie ma endpointu `/health` (patrz
      `api/router.py`), `/docs` (wbudowany Swagger UI FastAPI) wystarczy jako
      dowód, że aplikacja realnie wstała i odpowiada
- [ ] Realne sekrety w GitHub → Settings → Environments → `prod` — **nie
      uzupełnione** (nie mam do tego dostępu z tego środowiska). Bez nich
      `run_production.yml` przejdzie `container_smoke`, ale padnie na `ci`
      (brak `DOCKER_USERNAME`/`DOCKER_PASSWORD`/`REPOSITORY`)

## Zweryfikowane lokalnie

`infra/scripts/ci/ci_smoke.sh` odpalony bezpośrednio na tej maszynie
(`bash infra/scripts/ci/ci_smoke.sh`) — dokładnie ten sam skrypt, który
uruchamia `run_ci_test_containers.yml` w CI:

```
=== Layer 1: build obrazu produkcyjnego === ✔ (docker build)
=== Layer 2: import check (main + routery + modele) === ✔ (import ok)
=== Layer 3: boot uvicorna + probe /docs === ✔ (/docs odpowiada)
```

Składnia wszystkich 6 plików workflow zweryfikowana (`yaml.safe_load`).

## Nieprzetestowane / do zweryfikowania przy pierwszym realnym przebiegu

Brak dostępu do GitHub Actions z tego środowiska (i brak sekretów), więc:

- Pełny przebieg `run_production.yml` na realnym GitHub Actions (checkout,
  `astral-sh/setup-uv`, `docker login`, `ansible-playbook` na prawdziwy
  serwer) — **nie odpalony ani razu**, tylko sprawdzony wzrokowo i
  zweryfikowany co do składni
- `run_ci_test_local.yml` (serwis `postgres:16` + `make run_test`) — nie
  uruchomiony lokalnie w tej sesji celowo, bo wymagałoby to dotknięcia Twojej
  realnej lokalnej bazy dev (`env/local.env`); logika joba jest 1:1 tym, co
  już działa lokalnie u Ciebie przez `make run_test` z natywnym Postgresem
- `environment: prod` faktycznie przekazujące sekrety do reusable
  workflowów przez `secrets:` w `run_production.yml` — składniowo poprawne,
  ale bez realnego repo/environment na GitHubie nie do zweryfikowania stąd

## Status

Zaimplementowane w całości: 6 plików workflow + `infra/scripts/ci/ci_smoke.sh`,
smoke-test zweryfikowany lokalnie. Do odpalenia na żywo brakuje jeszcze
tylko uzupełnienia realnych sekretów w GitHub → Settings → Environments →
`prod` (`SSH_PRIVATE_KEY`, `ANSIBLE_PASSWORD`, `TARGET_HOST`, `SSH_USER`,
`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `REPOSITORY`) — patrz
[4 — infra](4-infra-done.md) sekcja "Co musisz uzupełnić sam".
