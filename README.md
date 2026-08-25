# arturscibor-server-FastAPI

Backend API portfolio [arturscibor.pl](https://arturscibor.pl/) — FastAPI,
architektura warstwowa (`api` / `core` / `database` / `config`), Postgres,
JWT, pełny pipeline CI/CD (GitHub Actions → Docker Hub → Ansible → Docker
Swarm, za wspólnym Traefikiem).

Frontend: [arturscibor-website-vue.js](https://github.com/1ChaLLengeR1/arturscibor-website-vue.js)

## Stos technologiczny

| Warstwa           | Technologia |
|--------------------|-------------|
| Framework          | **FastAPI** (Python 3.12+), **uvicorn** |
| ORM / baza         | **SQLAlchemy 2.0** (`Mapped[]`), **PostgreSQL**, **Alembic** |
| Walidacja / config | **Pydantic v2** + **pydantic-settings** |
| Auth               | **JWT** (PyJWT, access + refresh), **bcrypt** |
| Pliki              | Lokalny magazyn plików (własny odpowiednik S3, `static/files/`) |
| Testy              | **pytest** + `TestClient`, realny Postgres (nie mocki) |
| Pakiety / lint     | **uv** (`pyproject.toml` + `uv.lock`), **ruff** |
| Kontenery          | Docker (multi-stage, `uv sync --frozen`) |
| Orkiestracja       | **Docker Swarm** + **Traefik** (TLS Let's Encrypt, sieć współdzielona z innym projektem na tym samym serwerze) |
| Sekrety            | **Doppler** (aplikacja) + **ansible-vault** (infra) |
| Deploy             | **Ansible** (idempotentny playbook) |
| CI/CD              | **GitHub Actions** — testy → smoke obrazu → build+push → deploy |

Świadomie pominięte względem pełnego wzorca referencyjnego: Celery/Redis/
RabbitMQ (kolejki/cache — niepotrzebne w tej skali), Prometheus/Grafana
(observability, osobna decyzja na później), PgBouncer (Postgres natywnie na
hoście, jeden serwis).

## Architektura warstwowa

```
api/            ← HTTP: routing, walidacja wejścia/wyjścia, auth middleware
├── endpoints/     jeden plik = jedna operacja (get.py, create.py, update.py...)
├── schemas/       Pydantic — request/response per domena
├── middleware/     JWT auth middleware
├── router.py       spina wszystkie domeny w jeden APIRouter
└── response.py      spójny format odpowiedzi/błędów (bez hierarchii wyjątków)

core/           ← logika biznesowa, niezależna od HTTP i frameworka
├── handler/        orkiestruje repository + service dla jednej operacji
├── repository/      zapytania do bazy (per domena)
├── service/         cross-cutting (np. obsługa plików)
└── common/          jwt.py, bcrypt_password.py — niskopoziomowe, bez zależności domenowych

database/psql/  ← SQLAlchemy: modele, silnik, sesja per-request (get_db())
config/         ← pydantic-settings; env_prefix ARTURSCIBOR_BACKEND_, env/{tryb}.env
infra/          ← Dockerfile, docker-compose (Swarm), Ansible, skrypty CI/DB
```

Zasada: `api/` nie wie nic o SQL-u, `core/` nie wie nic o HTTP-ie,
`database/` nie wie nic o logice biznesowej. Jedna operacja (np. „dodaj
projekt") to zwykle: endpoint → handler → repository → model.

## Funkcjonalności

| Domena | Publiczne | Admin (JWT) |
|---|---|---|
| `auth` | login, refresh | — |
| `aboutme` | GET | update, zdjęcia |
| `contact` | wyślij wiadomość | lista, usuwanie |
| `cv` | pobierz plik | upload |
| `tools` | lista | CRUD + zdjęcia |
| `work` | lista | CRUD + pozycje + logo |
| `projects` | lista, szczegóły | CRUD + zdjęcia |
| `file` | — | init/upload/confirm/delete (generyczny magazyn dla powyższych) |

Wielojęzyczność (`pl`/`en`) na polach tekstowych przez `JSONB`
(`{"pl": "...", "en": "..."}`), walidowana Pydantikiem, bez osobnej tabeli
`Language`.

## Baza danych

`database/psql/models/`: `users`, `aboutme`, `contact`, `cv`, `tools`,
`work`, `projects`, `file` — migracje przez Alembic
(`make migration_up ENV=local|stg|prd`).

## Infrastruktura i deploy

Serwer produkcyjny: `server.arturscibor.pl`, Docker Swarm, Postgres
natywnie na hoście (nie w kontenerze). Traefik **współdzielony** z drugim
projektem na tym samym serwerze — ten sam stack, deployowany idempotentnie
z obu repo, żeby żadne nie musiało go "posiadać" na wyłączność.

Pipeline (`.github/workflows/run_production.yml`, na push do `main`):

```
container_smoke  →  ci (build + push obrazu)  →  cd (ansible-playbook → Swarm)
```

Sekrety aplikacji w Dopplerze (projekt `arturscibor_backend`, config `prd`),
sekrety infrastrukturalne w `infra/ansible/secrets.yml` (ansible-vault,
commitowany tylko zaszyfrowany).

## Uruchomienie lokalne

```bash
uv sync --all-extras
cp env/example-local.env env/local.env   # i uzupełnij
make run_app                              # uvicorn --reload
make run_test                             # pytest, wymaga lokalnego Postgresa
make migration_up ENV=local
```

Pełna lista komend w `Makefile`.

## Dokumentacja

Historia i decyzje projektowe: [`docs/roadmap.md`](docs/roadmap.md) (indeks
zadań) oraz wzorzec docelowy [`docs/ARCHITEKTURA.md`](docs/ARCHITEKTURA.md).
Każdy etap ma swój plik `docs/N-nazwa-done.md` z kontekstem, co i dlaczego
zostało zrobione tak, a nie inaczej.
