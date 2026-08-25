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
      `report` (podsumowanie + fail jeśli `cd` nie przeszedł). `ci`/`cd` NIE
      mają tu `environment:`/`secrets:` — GitHub odrzuca `environment:` na
      jobie, który jednocześnie woła reusable workflow przez `uses:`
      (potwierdzone realnie: pierwsza wersja z `environment: prod` na tych
      jobach dała "Invalid workflow file ... Unexpected value 'environment'"
      i run padał w 0s, bez grafu jobów). `environment: prod` siedzi więc w
      środku `run_ci_production.yml`/`run_cd_production.yml`, na jobie który
      faktycznie coś robi — patrz niżej
- [x] `run_ci_test_containers.yml` — wywołuje `infra/scripts/ci/ci_smoke.sh`
- [x] `run_ci_production.yml` — `environment: prod` na jobie `build_and_push`
      (patrz wyżej), stąd `${{ secrets.* }}` w krokach bierze się wprost z
      tego środowiska, bez przekazywania przez wołający job. Build
      (`infra/dockerfiles/production.dockerfile`) + push, nazwa obrazu z
      sekretu `REPOSITORY` (nie hardkodowana jak w projekcie referencyjnym —
      zgodnie z decyzją z pkt. 4 trzymania jej jako osobnego sekretu
      środowiska `prod`)
- [x] `run_cd_production.yml` — `environment: prod` na jobie `deploy`, tak
      samo jak wyżej. `ansible-playbook infra/ansible/playbook_deploy.yml`,
      renderuje `infra/ansible/inventory.ini` z `.example` (realny plik jest
      gitignored) + sekretów `TARGET_HOST`/`SSH_USER`, odszyfrowuje
      `secrets.yml` przez `ANSIBLE_PASSWORD`
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

## Zweryfikowane lokalnie i na żywo

`infra/scripts/ci/ci_smoke.sh` odpalony bezpośrednio na tej maszynie
(`bash infra/scripts/ci/ci_smoke.sh`) — dokładnie ten sam skrypt, który
uruchamia `run_ci_test_containers.yml` w CI:

```
=== Layer 1: build obrazu produkcyjnego === ✔ (docker build)
=== Layer 2: import check (main + routery + modele) === ✔ (import ok)
=== Layer 3: boot uvicorna + probe /docs === ✔ (/docs odpowiada)
```

Składnia wszystkich 6 plików workflow zweryfikowana (`yaml.safe_load`) —
ale to tylko generyczny YAML, nie schemat GitHub Actions. Realny przebieg na
GitHub Actions (Ty, na swoim repo) złapał to, czego `yaml.safe_load` złapać
nie mógł: `environment: prod` na jobie z `uses:` to poprawny YAML, ale
nieprawidłowy workflow wg GitHuba — `Invalid workflow file ... Unexpected
value 'environment'`, run padał w 0s bez grafu jobów. Poprawione (patrz
Kroki wyżej) i to jest właśnie powód, żeby to admit: reszta pipeline'u
(`docker login`, `ansible-playbook` na prawdziwy serwer, environment `prod`
faktycznie oddające sekrety) nadal nie przeszła pełnego realnego przebiegu
end-to-end — dopiero ten pierwszy krok (parsowalność workflow) jest
potwierdzony na żywo.

## Nieprzetestowane / do zweryfikowania przy pierwszym pełnym przebiegu

- Pełny przebieg `run_production.yml` do końca (build+push obrazu,
  `ansible-playbook` na prawdziwy serwer, deploy Traefika + backendu) —
  jeszcze nie zaobserwowany
- `run_ci_test_local.yml` (serwis `postgres:16` + `make run_test`) — nie
  uruchomiony lokalnie w tej sesji celowo, bo wymagałoby to dotknięcia Twojej
  realnej lokalnej bazy dev (`env/local.env`); logika joba jest 1:1 tym, co
  już działa lokalnie u Ciebie przez `make run_test` z natywnym Postgresem

## Status

Zaimplementowane w całości: 6 plików workflow + `infra/scripts/ci/ci_smoke.sh`,
smoke-test zweryfikowany lokalnie. Do odpalenia na żywo brakuje jeszcze
tylko uzupełnienia realnych sekretów w GitHub → Settings → Environments →
`prod` (`SSH_PRIVATE_KEY`, `ANSIBLE_PASSWORD`, `TARGET_HOST`, `SSH_USER`,
`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `REPOSITORY`) — patrz
[4 — infra](4-infra-done.md) sekcja "Co musisz uzupełnić sam".
