# 4 — Infra: `ansible/` `dockerfiles/` `scripts/`

## Kontekst

Pełna wersja wzorowana na `docs/ARCHITEKTURA.md` sekcja 12 (Ansible + Docker
Swarm + Traefik + sekrety w Dopplerze + vault dla sekretów infry), bez
Celery/Redis/RabbitMQ/Flower (nieużywane w tym projekcie) i bez
Prometheus/Grafana/exporterów (świadomie pominięte — observability, osobna
decyzja na później, nie część mechanizmu deployu).

Domeny w konfiguracji to placeholdery `example.com` — podmienisz jak będzie
znana docelowa domena. Sekrety aplikacji: **Doppler**, projekt
`arturscibor-server-fastapi`, config `prod`. Sekrety infrastrukturalne
(Doppler token, PAT, Docker Hub) w `infra/ansible/secrets.yml`, szyfrowane
`ansible-vault` — dokładnie jak w projekcie referencyjnym.

Przy okazji dodany prefiks `ARTURSCIBOR_BACKEND_` na wszystkich zmiennych
środowiskowych aplikacji (`config/settings.py` → `env_prefix`), analogicznie
do `WHERE_IS_WILLY_BACKEND_` w projekcie referencyjnym. Dotyczy to też
bundla w Dopplerze — klucze tam muszą być z tym samym prefiksem (patrz
`infra/ansible/tasks/secret_env.yml`).

## Struktura

```
infra/
├── ansible/
│   ├── playbook_deploy.yml
│   ├── inventory.ini.example    ← szablon, realny inventory.ini gitignored
│   ├── secrets.yml.example      ← szablon, realny secrets.yml commitowany TYLKO zaszyfrowany
│   └── tasks/
│       ├── checkout.yml          ← clone/update repo przez PAT
│       ├── networks.yml          ← overlay networks (traefik + backend)
│       ├── secret_env.yml        ← Doppler → content-hashed docker secret
│       ├── deploy.yml            ← docker login + stack deploy (traefik, backend)
│       └── cleanup.yml           ← docker image prune
├── dockerfiles/
│   ├── production.dockerfile     ← uv, multi-layer cache, CMD uvicorn
│   └── test.dockerfile           ← uv --all-extras, CMD pytest
├── compose/
│   ├── local.docker-compose.yaml           ← tylko Postgres, dev lokalny
│   ├── production.swarm.docker-compose.yaml ← backend + postgres, Swarm
│   └── traefik_production_stack.yaml        ← osobny stack, TLS Let's Encrypt
└── scripts/
    ├── vault.sh       ← encrypt/decrypt/view infra/ansible/secrets.yml
    ├── run_mode.sh    ← przełącza domyślny ENV_MODE w config/app.py (local wygoda)
    └── load_env.sh    ← source env/{name}.env + walidacja wymaganych zmiennych
```

## Kroki

- [x] `infra/dockerfiles/production.dockerfile` — zbudowany i przetestowany
      lokalnie (`docker build`), instaluje zależności przez `uv sync --frozen`,
      dwuwarstwowa struktura (deps osobno od źródła, cache-friendly)
- [x] `infra/dockerfiles/test.dockerfile` — zbudowany, uruchomiony
      (`docker run` → pytest realnie odpala się w kontenerze, 0 testów jak
      oczekiwane na tym etapie)
- [x] `infra/compose/local.docker-compose.yaml` — sam Postgres do dev
      lokalnego (backend nadal uruchamiany lokalnie przez `make run_app`,
      nie w kontenerze), spięty z `make docker_up`/`docker_down`
- [x] `infra/compose/production.swarm.docker-compose.yaml` — backend +
      postgres jako serwisy Swarm, sekrety przez content-hashed docker
      secret (`env_prod` jako stała nazwa usługi, realna nazwa zasobu przez
      `name: arturscibor_env_prod_${ENV_SECRET_VERSION}` — **UWAGA**: Compose
      nie interpoluje zmiennych w kluczach mapy, tylko w wartościach, stąd
      ten wzorzec zamiast wersjonowanej nazwy wprost w kluczu — to był
      realny błąd w pierwszej wersji, złapany przez `docker compose config`)
- [x] `infra/compose/traefik_production_stack.yaml` — osobny stack, TLS
      przez Let's Encrypt (tlsChallenge), montowany PRZED stackiem backendu
- [x] `infra/ansible/` — playbook + 5 plików tasków (checkout, networks,
      secret_env, deploy, cleanup), 1:1 z podziałem z projektu referencyjnego
- [x] `infra/ansible/secrets.yml.example` + `infra/ansible/inventory.ini.example`
      — szablony, **bez realnych wartości** (patrz sekcja "Co musisz uzupełnić" niżej)
- [x] `infra/scripts/vault.sh`, `run_mode.sh`, `load_env.sh`
- [x] `Makefile` — dodane `docker_up`, `docker_down`, `vault_encrypt`,
      `vault_decrypt`, `vault_view`
- [x] `.gitignore` — `infra/ansible/inventory.ini` (realny, z prawdziwym IP/userem)
- [ ] `infra/scripts/docker_entrypoint.sh` + skrypt migracji DB — **odłożone
      do 3.1**: nie ma jeszcze Alembic ani żadnych modeli, więc nie ma czego
      migrować; dopisujemy jak powstanie pierwsza migracja

## Świadome uproszczenia względem wzorca referencyjnego

- **Postgres jako serwis Swarm** (z wolumenem), nie natywnie na hoście +
  PgBouncer — mniej ruchomych części do postawienia na jednym serwerze
  portfolio. Można to później podnieść do wzorca referencyjnego, jeśli
  ruch/skala kiedyś to uzasadni.
- **Bez Prometheus/Grafana/Flower/exporterów** — observability to osobna
  decyzja, nie blokuje mechanizmu deployu. Łatwo dodać później jako kolejny
  stack.

## Nieprzetestowane / do zweryfikowania przy pierwszym realnym deployu

Nie mam tu serwera ani konta Doppler, więc części, które wymagają realnej
infrastruktury do walidacji, są zweryfikowane tylko "na papierze":

- Ansible playbook — brak `ansible`/`ansible-vault` w tym środowisku, więc
  **nie odpalony ani razu**, tylko sprawdzony wzrokowo pod kątem spójności
  z resztą (nazwy sieci, nazwy sekretów, kolejność tasków)
- Mapowanie kluczy z bundla Dopplera (`DB_USER`, `DB_PASSWORD`, `DB_NAME`,
  ...) na `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` oczekiwane przez
  oficjalny obraz `postgres` — zrobione w entrypoincie serwisu `postgres`
  w `production.swarm.docker-compose.yaml`, ale nieprzetestowane na żywym
  Swarmie

Co zweryfikowane realnie: **oba Dockerfile'y budują się i uruchamiają**
(`docker build` + `docker run`), **wszystkie 3 pliki compose są
schema-valid** (`docker compose config`, złapało i naprawiło błąd z
interpolacją zmiennej w kluczu sekretu).

## Co musisz uzupełnić sam (klucze/sekrety — nie generuję ich za Ciebie)

| Co | Gdzie | Skąd wziąć |
|---|---|---|
| `github_pat` | `infra/ansible/secrets.yml` (skopiuj z `.example`) | GitHub → Settings → Developer settings → Personal access tokens (scope: read repo) |
| `doppler_token` | `infra/ansible/secrets.yml` | Utwórz projekt `arturscibor-server-fastapi` w Dopplerze, config `prod`, wgraj tam wszystkie zmienne z `env/local.env` **z prefiksem `ARTURSCIBOR_BACKEND_`** (przeliczone na wartości produkcyjne — w tym `ARTURSCIBOR_BACKEND_DB_HOST=postgres`, bo w Swarmie łączysz się po nazwie usługi, nie `localhost`) + service token do configu `prod` |
| `docker_hub_username` / `docker_hub_password` | `infra/ansible/secrets.yml` | Docker Hub → Account Settings → Security → New Access Token (NIE hasło do konta) |
| Hasło do vault | zmienna środowiskowa `ANSIBLE_PASSWORD` przy `make vault_encrypt/decrypt/view` | Wymyślasz sam, zapisz bezpiecznie (menedżer haseł) — to samo hasło poda się CI w pkt. 5 jako sekret `ANSIBLE_PASSWORD` |
| `TARGET_HOST`, `SSH_USER` | `infra/ansible/inventory.ini` (skopiuj z `.example`, plik gitignored) | Adres/IP Twojego VPS i user SSH z uprawnieniami do Dockera |
| Klucz SSH do serwera | publiczny w `~/.ssh/authorized_keys` na VPS, prywatny jako sekret CI `SSH_PRIVATE_KEY` (pkt. 5) | `ssh-keygen`, wygenerowany przez Ciebie |
| Domena | `infra/compose/production.swarm.docker-compose.yaml` (label Traefika `Host(...)`) | Zamień `api.example.com` jak będzie znana |
| Email do Let's Encrypt | `infra/compose/traefik_production_stack.yaml` | Zamień `admin@example.com` na realny |
| Docker/Swarm na serwerze | ręcznie na VPS, jednorazowo, przed pierwszym deployem | `curl -fsSL https://get.docker.com \| sh`, potem `docker swarm init` |
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
budowa workflowów to osobne zadanie.

## Status

Szkielet + mechanizm deployu ukończone. Nieprzetestowane na żywej
infrastrukturze (patrz sekcja wyżej) — pierwsza realna weryfikacja nastąpi
przy pierwszym deployu, po pkt. 5 i po tym jak przynajmniej jedna domena z
3.1-3.5 będzie miała działający kod do wdrożenia.
