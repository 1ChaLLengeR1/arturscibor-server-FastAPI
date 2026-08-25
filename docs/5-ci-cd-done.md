# 5 — CI/CD (GitHub Actions)

## Kontekst

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 11, 1:1 przepisane z workflowów
projektu referencyjnego (`project-job-server-FastAPI`, katalog
`.github/workflows/`), dostosowane do decyzji z [4 — infra](4-infra-done.md):
pełny Ansible + Docker Swarm + Doppler, więc CI/CD też pełne
(test → container smoke → build+push → deploy), nie okrojone.

## Zdecydowane już (przy okazji pkt. 4) — i cofnięte w trakcie budowy pkt. 5

Pierwotna decyzja z pkt. 4: sekrety deployu (`SSH_PRIVATE_KEY`,
`ANSIBLE_PASSWORD`, `TARGET_HOST`, `SSH_USER`, `DOCKER_USERNAME`,
`DOCKER_PASSWORD`, `REPOSITORY`) w GitHub Actions **environment `prod`**, nie
jako zwykłe repo secrets. **Cofnięte przy realnym pierwszym przebiegu** —
patrz "Zweryfikowane lokalnie i na żywo" niżej: GitHub Environments
strukturalnie nie domykają się z architekturą "orkiestrator woła 3 osobne
pliki reusable workflow" (`run_production.yml` → `uses:`). Sekrety są teraz
**zwykłymi repository secretami** (Settings → Secrets and variables →
Actions → Repository secrets) — 1:1 jak w `project-job-server-FastAPI`. Jeśli
dodałeś je wcześniej pod environment `prod`, przenieś (dodaj od nowa pod
Repository secrets, wartości te same, stare pod environment możesz zostawić
nieużywane albo skasować).

`become_password` (hasło sudo, patrz pkt. 4) nie jest wśród tych sekretów —
żyje tylko wewnątrz zaszyfrowanego `infra/ansible/secrets.yml`.

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
      `report` (podsumowanie + fail jeśli `cd` nie przeszedł). `ci`/`cd`
      przekazują sekrety do reusable workflowów jawnie przez `secrets:`
      (repository secrets, patrz "Zdecydowane" wyżej) — bez `environment:`
      nigdzie w tym pliku
- [x] `run_ci_test_containers.yml` — wywołuje `infra/scripts/ci/ci_smoke.sh`
- [x] `run_ci_production.yml` — `on.workflow_call.secrets` (DOCKER_USERNAME,
      DOCKER_PASSWORD, REPOSITORY), przekazane przez `run_production.yml`.
      Build (`infra/dockerfiles/production.dockerfile`) + push, nazwa obrazu
      z sekretu `REPOSITORY` (nie hardkodowana jak w projekcie referencyjnym)
- [x] `run_cd_production.yml` — `on.workflow_call.secrets` (ANSIBLE_PASSWORD,
      SSH_PRIVATE_KEY, TARGET_HOST, SSH_USER), przekazane przez
      `run_production.yml`. `ansible-playbook infra/ansible/playbook_deploy.yml`,
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
- [x] Realne sekrety w GitHub → Settings → Secrets and variables → Actions →
      Repository secrets — uzupełnione (przez Ciebie; ja nie mam do tego
      dostępu z tego środowiska)

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
ale to tylko generyczny YAML, nie schemat GitHub Actions ani semantyka
sekretów, i to złapało dwa realne problemy dopiero na żywym GitHub Actions
(Ty, na swoim repo), niewidoczne lokalnie:

1. `environment: prod` na jobie z `uses:` to poprawny YAML, ale
   nieprawidłowy workflow wg GitHuba — `Invalid workflow file ... Unexpected
   value 'environment'`, run padał w 0s bez grafu jobów.
2. Po przeniesieniu `environment: prod` na sam reusable-workflow job (ten z
   `runs-on:`) workflow już się parsował i faktycznie oznaczał run jako
   `prod` w UI (widoczny badge/deployment) — ale `${{ secrets.* }}` w środku
   i tak wychodziło puste (`docker login -u "" ...`). Mimo poprawnej
   konfiguracji po stronie GitHuba (7 sekretów pod environment `prod`,
   nazwy 1:1) `environment:` na jobie wewnątrz reusable workflow daje tylko
   UI/reguły ochrony — NIE wstrzykuje sekretów środowiska do kontekstu
   `secrets.*` reusable workflow. Ten kontekst widzi tylko to, co jawnie
   zadeklarujesz w `on.workflow_call.secrets` i co caller jawnie przekaże —
   a caller nie może mieć `environment:` (punkt 1), więc sam nie ma dostępu
   do sekretów środowiska, żeby je przekazać dalej. Ślepy zaułek — stąd
   ostateczna decyzja: zwykłe repository secrets, bez `environment:` nigdzie.

Oba incydenty potwierdzone realnymi runami i screenami z Twojego GitHuba,
nie zgadywane.

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
sekrety uzupełnione jako repository secrets. `container_smoke` przechodzi na
żywo. Reszta pipeline'u (`ci` build+push, `cd` ansible-playbook na
prawdziwy serwer) jeszcze nie zaobserwowana end-to-end — patrz
"Nieprzetestowane" wyżej.
