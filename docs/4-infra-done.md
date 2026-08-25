# 4 — Infra: `ansible/` `dockerfiles/` `scripts/`

## Kontekst

Pełna wersja wzorowana na `docs/ARCHITEKTURA.md` sekcja 12 (Ansible + Docker
Swarm + Traefik + sekrety w Dopplerze + vault dla sekretów infry), bez
Celery/Redis/RabbitMQ/Flower (nieużywane w tym projekcie) i bez
Prometheus/Grafana/exporterów (świadomie pominięte — observability, osobna
decyzja na później, nie część mechanizmu deployu).

Domena: **`server.arturscibor.pl`** — wpisana już na stałe w
`infra/compose/production.swarm.docker-compose.yaml`, nie placeholder.
Repo na GitHubie: **`arturscibor/arturscibor_backend`**. Sekrety aplikacji:
**Doppler**, projekt `arturscibor_backend`, config **`prd`**. Sekrety
infrastrukturalne (Doppler token, PAT, Docker Hub, hasło sudo do serwera) w
`infra/ansible/secrets.yml`, szyfrowane `ansible-vault` — dokładnie jak w
projekcie referencyjnym (`project-job-server-FastAPI`).

**Traefik jest infrastrukturą współdzieloną** z `project-job-server-FastAPI`
na tym samym serwerze, na sieci overlay `traefik-public`. Zamiast zakładać,
że stoi tam "z zewnątrz" i tylko do niego dołączać, ten playbook — tak samo
jak playbook `project-job-server-FastAPI` — sam deployuje ten sam stack
Traefika (`tasks/deploy.yml` → `infra/compose/traefik_production_stack.yaml`,
stack name `traefik`), 1:1 tę samą konfigurację (ten sam resolver, ten sam
email, ta sama nazwa stacka). `docker stack deploy` jest idempotentny, więc
to bezpieczne: który by z tych dwóch projektów nie deployował jako ostatni,
po prostu reconciluje ten sam stan — nikt nie próbuje postawić drugiego
Traefika na portach 80/443, bo oba "stawiają" dokładnie ten sam. Jedyny
warunek: jeśli ta konfiguracja kiedyś się zmieni, trzeba zmienić ją w obu
repo naraz, inaczej oba CD będą się przeciągać między dwiema wersjami przy
każdym deployu.

Przy okazji dodany prefiks `ARTURSCIBOR_BACKEND_` na wszystkich zmiennych
środowiskowych aplikacji (`config/settings.py` → `env_prefix`), analogicznie
do prefiksu w projekcie referencyjnym. Dotyczy to też bundla w Dopplerze —
klucze tam muszą być z tym samym prefiksem (patrz
`infra/ansible/tasks/secret_env.yml`).

## Struktura

```
infra/
├── ansible/
│   ├── playbook_deploy.yml
│   ├── inventory.ini.example    ← szablon, realny inventory.ini gitignored
│   ├── secrets.yml               ← wypełniasz realnymi wartościami, szyfrujesz
│   │                                (ansible-vault) i DOPIERO WTEDY commitujesz
│   └── tasks/
│       ├── checkout.yml          ← clone/update repo przez PAT
│       ├── networks.yml          ← sieć overlay `traefik-public`, idempotentnie
│       │                            (współdzielona z project-job-server-FastAPI)
│       ├── secret_env.yml        ← Doppler → content-hashed docker secret
│       ├── deploy.yml            ← docker login + stack deploy Traefika + backendu
│       └── cleanup.yml           ← docker image prune
├── dockerfiles/
│   ├── production.dockerfile     ← uv, multi-layer cache, CMD uvicorn
│   └── test.dockerfile           ← uv --all-extras, CMD pytest
├── compose/
│   ├── traefik_production_stack.yaml ← 1:1 z project-job-server-FastAPI (patrz
│   │     Kontekst), deployowany PRZED stackiem backendu
│   └── production.swarm.docker-compose.yaml ← backend jako serwis Swarm,
│         dołącza do sieci `traefik-public`; Postgres NIE jest tu serwisem —
│         działa natywnie na hoście, backend łączy się przez `host.docker.internal`
└── scripts/
    ├── vault.sh       ← encrypt/decrypt/view infra/ansible/secrets.yml
    ├── run_mode.sh    ← przełącza domyślny ENV_MODE w config/app.py (local wygoda)
    ├── load_env.sh    ← source env/{name}.env + walidacja wymaganych zmiennych
    └── database/
        ├── migration_up.sh     ← database_up.sql + `alembic upgrade head`
        ├── migration_down.sh   ← DESTRUCTIVE (database_down.sql), potwierdzenie poza local
        ├── update_database.sh  ← idempotentny reseed singletonów (about_me, curriculum_vitae)
        └── restart.sh          ← pełny reset lokalnego schematu, tylko `local`
```

## Kroki

- [x] `infra/dockerfiles/production.dockerfile` — zbudowany i przetestowany
      lokalnie (`docker build`), instaluje zależności przez `uv sync --frozen`,
      dwuwarstwowa struktura (deps osobno od źródła, cache-friendly)
- [x] `infra/dockerfiles/test.dockerfile` — zbudowany, uruchomiony
      (`docker run` → pytest realnie odpala się w kontenerze)
- [x] `infra/compose/production.swarm.docker-compose.yaml` — backend jako
      serwis Swarm, sekrety przez content-hashed docker secret (`env_prd`
      jako stała nazwa usługi w compose, realna nazwa zasobu przez
      `name: arturscibor_env_prd_${ENV_SECRET_VERSION}` — **UWAGA**: Compose
      nie interpoluje zmiennych w kluczach mapy, tylko w wartościach, stąd
      ten wzorzec zamiast wersjonowanej nazwy wprost w kluczu — to był
      realny błąd w pierwszej wersji, złapany przez `docker compose config`).
      Dołącza do sieci `traefik-public` (patrz Kontekst), domena wpisana na
      stałe: `server.arturscibor.pl`
- [x] Postgres **natywnie na hoście**, nie jako serwis Swarm (tak samo jak w
      projekcie referencyjnym i jak w local dev) — backend łączy się przez
      `host.docker.internal` (`ARTURSCIBOR_BACKEND_DB_HOST=host.docker.internal`
      w Dopplerze, config `prd`)
- [x] `infra/ansible/` — playbook + 5 plików tasków (checkout, networks,
      secret_env, deploy, cleanup), 1:1 z podziałem z projektu referencyjnego,
      **w tym deploy Traefika** — ten sam stack co w `project-job-server-FastAPI`,
      patrz Kontekst; `become: true` + `ansible_become_pass` czytany z
      `secrets.yml` (hasło sudo do usera SSH na serwerze)
- [x] `infra/compose/traefik_production_stack.yaml` — 1:1 kopia stacka
      Traefika z `project-job-server-FastAPI` (ten sam resolver `myresolver`,
      ten sam email, ta sama nazwa stacka `traefik`) — deployowany PRZED
      stackiem backendu
- [x] `infra/ansible/secrets.yml` + `infra/ansible/inventory.ini.example`
      — szablony, **bez realnych wartości** (patrz sekcja "Co musisz uzupełnić" niżej)
- [x] `infra/scripts/vault.sh`, `run_mode.sh`, `load_env.sh`
- [x] `infra/scripts/database/{migration_up,migration_down,update_database,restart}.sh`
      — działają na realnym Alembicu (patrz 3.1+ i `database_up.sql`/`database_down.sql`),
      ale odpalane **ręcznie** (np. `make migration_up ENV=prd`) — nie ma
      jeszcze automatycznego kroku migracji w playbooku deployu, patrz punkt niżej
- [x] `Makefile` — `migration_up`, `migration_down`, `migration_restart`,
      `update_database` (parametr `ENV`, domyślnie `local`), `vault_encrypt`,
      `vault_decrypt`, `vault_view`
- [x] `.gitignore` — `infra/ansible/inventory.ini` (realny, z prawdziwym IP/userem)
- [ ] `infra/scripts/docker_entrypoint.sh` — auto-migracja przy starcie
      kontenera produkcyjnego, **wciąż nie zrobione**: migracje na razie
      trzeba odpalić ręcznie (`migration_up.sh prd`) przed/po deployu, nie są
      częścią `tasks/deploy.yml`
- [ ] Lokalny Postgres w Dockerze (`infra/compose/local.docker-compose.yaml`
      + `make docker_up`/`docker_down`) — **nie istnieje**, mimo że
      wcześniejsza wersja tego dokumentu to zakładała jako zrobione; lokalnie
      Postgres stoi natywnie na hoście (`env/local.env` → `DB_HOST=localhost`),
      tak samo jak docelowo w produkcji — jeśli kiedyś zajdzie potrzeba
      konteneryzacji lokalnego Postgresa, to osobne zadanie

## Świadome uproszczenia względem wzorca referencyjnego

- **Bez Prometheus/Grafana/Flower/exporterów** — observability to osobna
  decyzja, nie blokuje mechanizmu deployu. Łatwo dodać później jako kolejny
  stack.
- **Traefik jako współdzielona infra, deployowana z dwóch repo naraz** —
  zamiast trzymać go w jednym "właścicielskim" repo i zakładać, że drugi
  projekt się do niego dołączy z zewnątrz, oba repo deployują identyczny
  stack pod tą samą nazwą (`docker stack deploy` jest idempotentny). Prostsze
  niż wydzielanie Traefika do osobnego, trzeciego repo/mechanizmu deployu —
  ale wymaga pilnowania, żeby obie kopie configu nie rozjechały się przy
  edycji (patrz Kontekst).

## Nieprzetestowane / do zweryfikowania przy pierwszym realnym deployu

Nie mam tu serwera ani konta Doppler, więc części, które wymagają realnej
infrastruktury do walidacji, są zweryfikowane tylko "na papierze":

- Ansible playbook — brak `ansible`/`ansible-vault` w tym środowisku, więc
  **nie odpalony ani razu**, tylko sprawdzony wzrokowo pod kątem spójności
  z resztą (nazwy sieci, nazwy sekretów, kolejność tasków, `become_password`)
- Mapowanie kluczy z bundla Dopplera (`ARTURSCIBOR_BACKEND_DB_HOST=host.docker.internal`,
  ...) — opisane w komentarzu `production.swarm.docker-compose.yaml`, ale
  nieprzetestowane na żywym Swarmie
- Współdzielony deploy Traefika z dwóch repo — zakładam, że
  `docker stack deploy` na tę samą nazwę stacka (`traefik`) z identycznym
  configiem faktycznie jest no-opem, jeśli `project-job-server-FastAPI` już
  go wcześniej wdrożył (tak działa Swarm w teorii), ale nie zweryfikowane
  na żywym klastrze

Co zweryfikowane realnie: **oba Dockerfile'y budują się i uruchamiają**
(`docker build` + `docker run`), plik compose jest schema-valid
(`docker compose config`, złapało i naprawiło błąd z interpolacją zmiennej
w kluczu sekretu).

## Co musisz uzupełnić sam (klucze/sekrety — nie generuję ich za Ciebie)

| Co | Gdzie | Skąd wziąć |
|---|---|---|
| `github_pat` | `infra/ansible/secrets.yml` | GitHub → Settings → Developer settings → Personal access tokens (scope: read repo, na `arturscibor/arturscibor_backend`) |
| `doppler_token` | `infra/ansible/secrets.yml` | Utwórz projekt `arturscibor_backend` w Dopplerze, config `prd`, wgraj tam wszystkie zmienne z `env/local.env` **z prefiksem `ARTURSCIBOR_BACKEND_`** (przeliczone na wartości produkcyjne — w tym `ARTURSCIBOR_BACKEND_DB_HOST=host.docker.internal`) + service token do configu `prd` |
| `docker_hub_username` / `docker_hub_password` | `infra/ansible/secrets.yml` | Docker Hub → Account Settings → Security → New Access Token (NIE hasło do konta) |
| `become_password` | `infra/ansible/secrets.yml` | Hasło sudo usera SSH na serwerze (`ansible_become_pass`). **Nie dubluj go w GitHub Actions secrets** — żyje tylko wewnątrz zaszyfrowanego `secrets.yml`, odszyfrowywanego w CI przez `ANSIBLE_PASSWORD` (to osobny sekret CI — hasło do vaulta, nie do sudo) |
| Hasło do vault | zmienna środowiskowa `ANSIBLE_PASSWORD` przy `make vault_encrypt/decrypt/view` | Wymyślasz sam, zapisz bezpiecznie (menedżer haseł) — to samo hasło poda się CI w pkt. 5 jako sekret `ANSIBLE_PASSWORD` |
| `TARGET_HOST`, `SSH_USER` | `infra/ansible/inventory.ini` (skopiuj z `.example`, plik gitignored) | Adres/IP VPS i user SSH z uprawnieniami do Dockera — ten sam serwer, na którym już stoi `project-job-server-FastAPI` + Traefik |
| Klucz SSH do serwera | publiczny w `~/.ssh/authorized_keys` na VPS, prywatny jako sekret CI `SSH_PRIVATE_KEY` (pkt. 5) | `ssh-keygen`, wygenerowany przez Ciebie |
| Docker/Swarm na serwerze | już jest (Swarm zainicjowany pod `project-job-server-FastAPI`) — nic do zrobienia, chyba że to inny serwer | `curl -fsSL https://get.docker.com \| sh`, potem `docker swarm init` |
| `doppler` CLI na serwerze | ręcznie na VPS (używane przez `tasks/secret_env.yml`) | https://docs.doppler.com/docs/install-cli |

Po wypełnieniu `infra/ansible/secrets.yml`:
```
ANSIBLE_PASSWORD=twoje-haslo make vault_encrypt
```
i dopiero WTEDY commitujesz — plik jest wtedy zaszyfrowany, bezpieczny do gita.

## Do zapamiętania na pkt. 5 (CI/CD)

GitHub Actions będzie miał environment `prod` (Settings → Environments) z
sekretami: `SSH_PRIVATE_KEY`, `ANSIBLE_PASSWORD`, `TARGET_HOST`, `SSH_USER`,
`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `REPOSITORY` — decyzja podjęta teraz,
budowa workflowów to osobne zadanie. **Hasło sudo (`become_password`) nie
jest wśród nich** — nie ma dla niego osobnego sekretu CI, bo siedzi już
zaszyfrowane wewnątrz `secrets.yml` i odszyfrowuje się razem z resztą przez
`ANSIBLE_PASSWORD`.

## Status

Szkielet + mechanizm deployu ukończone, dociągnięte o realne dane (domena,
nazwa repo, Doppler, współdzielony Traefik) w miejsce placeholderów.
Nieprzetestowane na żywej infrastrukturze (patrz sekcja wyżej) — pierwsza
realna weryfikacja nastąpi przy pierwszym deployu, po pkt. 5.
