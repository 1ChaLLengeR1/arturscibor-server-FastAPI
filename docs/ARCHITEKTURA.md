# Architektura projektu WhereIsWheely (backend FastAPI)

> Dokument opisuje pełną architekturę tego projektu: warstwy kodu, konwencje, tooling,
> testy, CI/CD i infrastrukturę deploy. Służy jako **wzorzec referencyjny** przy
> refaktoryzacji innych projektów FastAPI (np. starych projektów opartych o
> `pip install -r requirements.txt`) do tej struktury.

---

## Spis treści

1. [Stos technologiczny](#1-stos-technologiczny)
2. [Standard toolingu: uv + Makefile](#2-standard-toolingu-uv--makefile)
3. [Struktura katalogów projektu](#3-struktura-katalogów-projektu)
4. [Architektura warstwowa](#4-architektura-warstwowa)
5. [Warstwa `api/`](#5-warstwa-api)
6. [Warstwa `core/` — serce backendu](#6-warstwa-core--serce-backendu)
7. [Konfiguracja `config/`](#7-konfiguracja-config)
8. [`main.py` — złożenie aplikacji](#8-mainpy--złożenie-aplikacji)
9. [Baza danych `database/psql/` + Alembic](#9-baza-danych-databasepsql--alembic)
10. [Testy `tests/` + pytest.ini](#10-testy-tests--pytestini)
11. [CI/CD — GitHub Actions `.github/workflows/`](#11-cicd--github-actions-githubworkflows)
12. [Infrastruktura `infra/`](#12-infrastruktura-infra)
13. [Zmienne środowiskowe `env/`](#13-zmienne-środowiskowe-env)
14. [Konwencje nazewnictwa](#14-konwencje-nazewnictwa)
15. [Checklista: dodawanie nowej funkcjonalności](#15-checklista-dodawanie-nowej-funkcjonalności)
16. [Znane rozbieżności / uwagi porządkowe](#16-znane-rozbieżności--uwagi-porządkowe)

---

## 1. Stos technologiczny

| Element          | Technologia                                                      |
|------------------|------------------------------------------------------------------|
| Framework        | **FastAPI** (>=0.116), Python **3.13** (`>=3.13,<3.15`)          |
| Serwer           | uvicorn (dev) / **gunicorn + UvicornWorker** (prod)              |
| ORM              | **SQLAlchemy 2.0** z `Mapped[]` type hints                       |
| Baza danych      | **PostgreSQL** (JSONB dla i18n, UUID primary keys) + PgBouncer   |
| Migracje         | **Alembic**                                                      |
| Cache            | **Redis** (JSON + kompresja zlib)                                |
| Kolejka zadań    | **Celery** (broker: RabbitMQ, backend: Redis) + Celery Beat      |
| Auth             | JWT (PyJWT) — access + refresh tokens, rewokacja przez DB        |
| Hasła            | bcrypt                                                           |
| Rate limiting    | **slowapi** (storage w Redis — limity wspólne dla replik)        |
| Walidacja        | Pydantic v2 + **pydantic-settings**                              |
| Płatności        | Stripe (checkout + webhooki)                                     |
| Kurier           | InPost ShipX (async httpx client z retry)                        |
| Mail             | fastapi-mail (szablony HTML w `core/templates/emails/`)          |
| Observability    | Sentry, Prometheus (`/metrics`), JSON logging, Grafana, Flower   |
| Testy            | **pytest** + TestClient (realny Postgres i Redis)                |
| Pakiety          | **uv** (`pyproject.toml` + `uv.lock`) — NIE pip/requirements.txt |
| Lint/format      | **ruff** + ruff-format (pre-commit)                              |
| CI/CD            | GitHub Actions → Docker Hub → Ansible → **Docker Swarm**         |

---

## 2. Standard toolingu: uv + Makefile

**To jest fundament projektu.** Zależności zarządza **uv** (nie pip, nie
requirements.txt). Wszystko definiuje `pyproject.toml` + lockfile `uv.lock`,
a codzienne komendy są opakowane w **Makefile**.

### 2.1 pyproject.toml

- Nazwa: `whereiswilly_backend`, build system: setuptools; pakiety wykrywane z
  `api*, core*, config*, database*, infra*`.
- **Zależności główne**: fastapi, uvicorn, sqlalchemy, psycopg2-binary, alembic,
  pydantic[email], pydantic-settings, PyJWT, bcrypt, redis, celery, stripe,
  fastapi-mail, httpx, slowapi, sentry-sdk[fastapi], prometheus-client,
  python-json-logger.
- **Extras (grupy opcjonalne)**:
  - `test` — pytest, pytest-asyncio, pytest-cov, pytest-xdist, pytest-mock,
    faker, factory-boy, hypothesis, locust…
  - `dev` — ruff, pre-commit, mypy
  - `prod` — gunicorn
- **Ruff**: `line-length=120`, `target-version=py313`, reguły
  `E,F,W,I,N,UP,B,SIM`; ignorowane `B008` (FastAPI `Depends` w default arg),
  per-file-ignores dla `alembic/**` i `api/router.py` (E402).
- **Mypy**: plugin `pydantic.mypy`, nie-strict (wybrane flagi).

### 2.2 Makefile — targety

| Target                     | Komenda / opis                                                            |
|----------------------------|---------------------------------------------------------------------------|
| `make install`             | `uv sync --all-extras` — pełna instalacja środowiska                      |
| `make clean`               | usuwa `.venv`, `uv.lock`, cache pytest, `__pycache__`                     |
| `make run_app`             | `uv run uvicorn main:app --reload --port 4444`                            |
| `make docker_up` / `docker_down` | lokalna infra (Redis + RabbitMQ) przez docker compose              |
| `make run_celery_worker`   | `uv run celery -A config.celery worker --pool=solo` (Windows-friendly)    |
| `make run_celery_beat`     | `uv run celery -A config.celery beat`                                     |
| `make run_test`            | `uv run pytest -s -v` (domyślny filtr markerów z pytest.ini)              |
| `make run_test_integration`| pytest `-m "not slow and not full_integration and not api_integration"` — **używane w CI** |
| `make run_test_full`       | wszystko, łącznie z zewnętrznymi API (kasuje addopts)                     |
| `make run_test_full_integration` | tylko `-m full_integration` (sandbox InPost — realne etykiety)      |
| `make run_test_api_integration`  | tylko `-m api_integration` (Sentry ingest, InPost health)           |
| `make migration_up ENV=local`    | skrypt `infra/scripts/database/migration_up.sh`                     |
| `make migration_down ENV=local`  | skrypt `migration_down.sh` (destrukcyjny — DROP tabel)              |
| `make migration_restart ENV=local` | pełny reset schematu (`restart.sh`)                               |
| `make vault_decrypt/encrypt/view` | ansible-vault na `infra/ansible/secrets.yml` (hasło w env `ANSIBLE_PASSWORD`) |

Zmienna `ENV ?= local` steruje środowiskiem migracji (`local|stg|prod`).

### 2.3 Pre-commit

`.pre-commit-config.yaml`: `trailing-whitespace`, `end-of-file-fixer`,
`check-yaml`, `check-toml`, `check-merge-conflict`, `check-added-large-files`
(max 500 kB), `detect-private-key` oraz **ruff** (`--fix`) + **ruff-format**.
Projekt NIE używa black/isort/flake8 — wszystko robi ruff.

---

## 3. Struktura katalogów projektu

```
.
├── main.py                     ← złożenie aplikacji FastAPI (entrypoint)
├── pyproject.toml              ← zależności, extras, ruff, mypy (standard uv)
├── uv.lock                     ← lockfile uv
├── Makefile                    ← wszystkie codzienne komendy
├── pytest.ini                  ← globalna konfiguracja pytest (markery!)
├── alembic.ini + alembic/      ← migracje bazy danych
├── api/                        ← warstwa HTTP (endpointy, schematy, middleware)
│   ├── endpoints/              ← routery: jeden plik = jeden endpoint
│   │   └── urls.py             ← WSZYSTKIE ścieżki jako stałe
│   ├── middleware/             ← JWTAuthenticationMiddleware, CartIdentity
│   ├── schemas/                ← payloady + response schemas (Pydantic)
│   ├── router.py               ← centralna rejestracja wszystkich routerów
│   ├── response.py             ← ApiResponse / ApiErrorResponse / ApiErrorData
│   ├── exception_handlers.py   ← globalne handlery AppException / Exception
│   └── validators.py           ← wspólne walidatory (np. validate_i18n)
├── core/                       ← serce backendu (logika biznesowa)
│   ├── handler/                ← orchestracja + cache (warstwa nad repository)
│   ├── service/                ← logika wielotabelowa / zewnętrzne API
│   ├── process/                ← przetwarzanie danych PRZED funkcjami _psql
│   ├── repository/
│   │   ├── psql/               ← funkcje _psql (czyste zapytania DB)
│   │   └── file/               ← repozytoria plikowe (np. technical_pause JSON)
│   ├── tasks/                  ← zadania asynchroniczne Celery
│   ├── common/                 ← jwt, bcrypt, cart_token, http_retry
│   ├── exceptions/             ← AppException + hierarchia
│   ├── templates/emails/       ← szablony HTML maili
│   └── utils/                  ← drobne narzędzia
├── config/                     ← konfiguracja aplikacji
│   ├── settings.py             ← pydantic-settings, czyta env/*.env
│   ├── app.py                  ← ENV_MODE, BASE_DIR
│   ├── redis.py                ← klient Redis + cache API (zlib)
│   ├── rate_limit.py           ← slowapi limiter
│   ├── celery.py               ← celery_app + beat schedule
│   ├── gunicorn.py             ← konfiguracja produkcyjna serwera
│   ├── mail.py                 ← fastapi-mail ConnectionConfig
│   ├── metrics.py              ← Prometheus + RequestLoggingMiddleware
│   ├── sentry.py               ← Sentry + ErrorObservabilityMiddleware
│   └── swagger_description/    ← opis, tagi i summary Swaggera
├── database/psql/              ← wszystko o bazie danych
│   ├── database.py             ← engine, get_db, managed_session
│   ├── base.py                 ← declarative Base
│   ├── models/                 ← modele SQLAlchemy (jeden plik = jedna domena)
│   └── sql/                    ← database_up.sql / database_down.sql
├── tests/                      ← testy — lustrzana struktura katalogów
├── env/                        ← pliki .env per środowisko (gitignored)
├── infra/
│   ├── ansible/                ← deploy (playbook + taski + vault secrets)
│   ├── dockerfiles/            ← production/test dockerfile, compose, swarm
│   └── scripts/                ← ci_smoke, run_tests, migracje DB, vault
├── runners/                    ← skrypty pomocnicze (np. hash hasła admina)
├── static/                     ← pliki statyczne (obrazy produktów/kategorii)
└── docs/                       ← dokumentacja, flow-notes, runbooki
```

---

## 4. Architektura warstwowa

Każda funkcjonalność przechodzi przez trzy warstwy w dół i trzy w górę:

```
api/endpoints/{domain}/{action}.py        ← HTTP, walidacja body, swagger, auth
        ↓ wywołuje handler
core/handler/{domain}/{action}.py         ← logika, cache Redis, orchestracja
        ↓ wywołuje _psql
core/repository/psql/{domain}/{action}.py ← zapytania DB, mapowanie na dataclass
```

**Zasady twarde:**

- **Nigdy nie pomijaj warstw.** Endpoint nie wywołuje `_psql` bezpośrednio.
  Handler nie zna FastAPI ani `HTTPException`.
- Do `_psql` dane wchodzą **już zwalidowane** (walidacja jest w Pydantic payload
  na poziomie endpointu, ewentualnie w `core/process/`).
- Cache Redis żyje **w handlerze**, nie w `_psql`.
- Jeśli logika wybiega poza jedną domenę (kilka tabel, zewnętrzne API, mail) —
  wchodzi warstwa `core/service/`.
- Przetwarzanie/normalizacja danych przed zapisem — `core/process/`.
- Zadania asynchroniczne — `core/tasks/` (Celery).

### 4.1 Tuple Response Pattern

Każda funkcja — handler, service, process i `_psql` — zwraca tuple
`(result, error, ok)`:

```python
def example_psql(..., db_session: Session | None = None) -> tuple[ResultType | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            # ... logika
            return result, None, True
    except IntegrityError:
        return None, ApiErrorData(
            message="...",
            type_module="example_psql",
            type_error="integrity_error",
            key_type_error="IntegrityError",
        ), False
    except Exception as e:
        return None, ApiErrorData(
            message=str(e),
            type_module="example_psql",
            type_error="exception",
            key_type_error="Exception",
        ), False
```

W handlerze propagacja:

```python
result, err, ok = example_psql(...)
if not ok:
    return None, err, False
return result, None, True
```

W endpoincie mapowanie na HTTP:

```python
data, error, success = handler_example(...)
if not success:
    status_code = 409 if error.key_type_error == "IntegrityError" else 400
    return JSONResponse(status_code=status_code, content=ApiErrorResponse(...).model_dump())
return ApiResponse(status="SUCCESS", status_code=201, data=SomeSchema(**asdict(data)))
```

**Konwencja `key_type_error`:**

| Wartość            | Kiedy                          | Typowy HTTP |
|--------------------|--------------------------------|-------------|
| `"IntegrityError"` | duplikat, naruszenie FK        | 409         |
| `"NotFound"`       | brak rekordu                   | 404         |
| `"Exception"`      | nieobsłużony wyjątek           | 400/500     |

Obok tuple pattern istnieje **nowsza hierarchia wyjątków** (`core/exceptions/`):
`AppException` (500) → `NotFoundError` (404), `ConflictError` (409),
`IntegrityViolationError`, `ExternalServiceError` (502), `DatabaseError` —
obsługiwana przez globalne exception handlery. Oba wzorce współistnieją;
`ErrorObservabilityMiddleware` domyka lukę w metrykach/Sentry dla ścieżki tuple.

### 4.2 Typy danych między warstwami

- **Wewnętrzne response** (repository → handler → endpoint):
  **`@dataclass`** w `core/repository/psql/{domain}/response.py` + konwerter
  `_to_{domain}_response(model) -> {Domain}Response`. **Standardem jest
  dataclass**; w nielicznych przypadkach dopuszczalny `TypedDict`, ale domyślnie
  zawsze dataclass.
- **Payloady (request body)** i **response data** (co idzie w
  `ApiResponse.data`) — Pydantic `BaseModel` w `api/schemas/{domain}/`.
- Konwersja dataclass → Pydantic w endpoincie: `SomeResponseData(**asdict(data))`.

---

## 5. Warstwa `api/`

### 5.1 Endpointy — `api/endpoints/{scope}/{domain}/{action}.py`

**Jeden plik = jeden router z jedną funkcją.** Scope to `admin/`, `auth/`,
`user/` lub katalog publiczny (np. `product/`, `cart/`).

```python
router = APIRouter()

@router.post(
    ADMIN_PRODUCTS_CREATE,                      # ← stała z urls.py, nigdy string
    summary="[Admin] Utwórz produkt",           # ← prefix roli obowiązkowy
    response_model=ApiResponse[ProductResponseData],
    responses={                                  # ← wszystkie kody błędów
        409: {"model": ApiErrorResponse, "description": "Slug już istnieje"},
        403: {"model": ApiErrorResponse, "description": "Brak uprawnień"},
        500: {"model": ApiErrorResponse, "description": "Nieoczekiwany błąd serwera"},
    },
    status_code=201,
    tags=["Admin/Products"],                     # ← grupowanie w Swaggerze
)
def api_admin_create_product(
    body: ProductCreatePayload,
    current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
    db: Session = Depends(get_db),
) -> ApiResponse[ProductResponseData] | JSONResponse:
    ...
```

**Swagger jest obowiązkowy** — każdy endpoint musi mieć `summary` (z prefiksem
roli `[Admin]`/`[User]`/`[Guest]`/`[Public]`), pełne `responses` i `tags`.

### 5.2 URL constants — `api/endpoints/urls.py`

Wszystkie ścieżki jako stałe w jednym pliku. Wzorzec
`/api/v1/{scope}/{resource}/{action}`:

| Operacja      | Wzorzec URL                 |
|---------------|-----------------------------|
| GET lista     | `/collection`               |
| GET jeden     | `/{id}/one`                 |
| POST          | `/create`                   |
| PATCH         | `/{id}/update`              |
| DELETE        | `/{id}/delete`              |

Sub-resource nested pod rodzicem
(`/api/v1/admin/products/{product_id}/stock/create`), standalone resource z
własnym ID (`/api/v1/admin/variants/{variant_id}/update`).

### 5.3 Router centralny — `api/router.py`

Jeden `api_router = APIRouter()`; każdy plik endpointu importowany jako alias i
rejestrowany `api_router.include_router(module.router)` (~160 rejestracji),
pogrupowane sekcjami z komentarzami per domena. **Kolejność rejestracji bywa
istotna** — trasy statyczne (np. `recently_purchased`) rejestrowane PRZED
trasami z parametrem (`/{product_id}`), żeby nie zostały przechwycone.

### 5.4 Response envelope — `api/response.py`

```python
class ApiResponse(BaseModel, Generic[DATA, ADDITIONALS]):
    status: Literal["SUCCESS", "ERROR", "STOCK_CONFLICT"]
    status_code: int
    data: Optional[DATA] = None
    additional: Optional[ADDITIONALS] = None

class ApiErrorData(BaseModel):
    message: str
    type_module: str      # nazwa funkcji, w której powstał błąd
    type_error: str
    key_type_error: str   # "IntegrityError" | "NotFound" | "Exception"

class ApiErrorResponse(BaseModel, Generic[ADDITIONALS]):
    status: Literal["ERROR"] = "ERROR"
    status_code: int
    data: ApiErrorData
    additional: Optional[ADDITIONALS] = None
```

Specjalny status `STOCK_CONFLICT` (HTTP 200) sygnalizuje przy checkout, że
koszyk wymaga rewizji stanów magazynowych.

### 5.5 Middleware — `api/middleware/`

- **`Authentication.py` → `JWTAuthenticationMiddleware(HTTPBearer)`** — to
  dependency (używane w `Depends()`), nie klasyczne ASGI middleware. Przepływ:
  Bearer token → `decode_jwt` (weryfikacja podpisu) → wymagany claim `jti` →
  sprawdzenie **aktywnego rekordu tokena w DB** (`one_active_token_by_jti_psql`
  — to jest mechanizm rewokacji: logout/refresh unieważnia rekord) → zgodność
  `user_id` z claimem → **cache usera w Redis** (`auth_user:{user_id}`, TTL
  max 300 s) → ban check (403) → weryfikacja ról (`roles=["admin"]` itd., 403
  przy braku uprawnień). Zwraca dict z danymi usera.
  Wariant **`OptionalJWTAuthenticationMiddleware`** — brak nagłówka → `None`
  (gość); token obecny ale zepsuty → 401.
- **`CartIdentity.py` → `cart_identity_dependency`** — dwuścieżkowa tożsamość
  koszyka: `Authorization: Bearer` (zalogowany, pełna walidacja jak wyżej) LUB
  nagłówek `X-Cart-Token` (gość — token `{uuid}.{hmac-sha256}` weryfikowany
  sekretem `cart_token_secret`). Zwraca dataclass
  `CartIdentity(user_id, session_token)`.

### 5.6 Schemas — `api/schemas/{domain}/`

Payloady i response schemas Pydantic. Proste domeny: wszystko w `__init__.py`;
większe (product): osobne pliki `create.py`, `update.py`. Pola i18n walidowane
przez `validate_i18n` z `api/validators.py` (dict z dokładnie kluczami
`pl` i `en`, niepuste stringi).

### 5.7 Exception handlers — `api/exception_handlers.py`

`register_exception_handlers(app)` rejestruje: (1) handler `AppException` —
mapuje na envelope błędu + `request_id` w `additional`, bumpuje metrykę
`app_exceptions_total`; (2) handler bare `Exception` — loguje traceback,
wysyła do Sentry, zwraca generyczne 500 bez wycieku treści wyjątku.
`HTTPException` i `RequestValidationError` celowo zostają przy domyślnych
handlerach FastAPI (kontrakt z frontendem).

---

## 6. Warstwa `core/` — serce backendu

### 6.1 `core/handler/{domain}/{action}.py`

Handler odpowiada za: (1) wywołanie `_psql` (jednego lub kilku), (2)
**invalidację cache Redis po zapisach**, (3) propagację tuple pattern.

```python
def handler_create_product(..., db_session: Session | None = None):
    try:
        result, err, ok = create_product_psql(..., db_session=db_session)
        if not ok:
            return None, err, False
        delete_cache_by_prefix("product:collection:")
        delete_cache_by_prefix("product:admin:collection:")
        return result, None, True
    except Exception as e:
        return None, ApiErrorData(message=str(e), type_module="handler_create_product",
                                  type_error="exception", key_type_error="Exception"), False
```

Gdy operacja wymaga kilku `_psql` (np. add_cart_item: znajdź/utwórz koszyk →
dodaj item), to **nadal jest handler** — jeden plik = jedna operacja, bez
osobnych klas service.

Odczyt z cache w handlerze:

```python
_CACHE_TTL = 120
cached = get_cache_data(cache_key)
if cached is not None:
    return [SomeResponse(**item) for item in cached], None, True
result, err, ok = some_psql(...)
if not ok:
    return None, err, False
set_cache_data(cache_key, [dataclasses.asdict(item) for item in result], timeout=_CACHE_TTL)
return result, None, True
```

### 6.2 `core/service/{domain}/`

Warstwa dla logiki, która **wybiega poza jedną domenę/tabelę lub strzela do
zewnętrznych API**. Przykłady w projekcie:

- `service/order/` — create/cancel/reorder (orkiestracja: pricing, stock
  decrement/restore, discount code, payment),
- `service/stripe/` — `webhook/construct_event.py` (weryfikacja podpisu — to
  granica auth webhooka), `events/` (obsługa `checkout_session_completed`,
  `payment_intent_payment_failed`), `handler/create.py` (checkout session),
- `service/inpost/` — async klient ShipX (`client.py`: create/get/cancel
  shipment, get label; httpx + `request_with_retry`, rozróżnienie operacji
  idempotentnych od nieidempotentnych, żeby nie zduplikować płatnej etykiety),
- `service/mail/` — wysyłka maili z szablonów (`send_welcome`,
  `send_order_confirmation`, `send_reset_password`, …),
- `service/auth/login.py`, `service/payment/`, `service/b2b_application/`.

Serwisy również zwracają tuple `(result, err, ok)`.

### 6.3 `core/process/{domain}/`

**Przetwarzanie/normalizacja danych PRZED funkcjami `_psql`** — czysta logika
transformacji bez dostępu do DB. Przykłady: `process/cart/check.py`
(weryfikacja stanów koszyka), `process/categories/` (przygotowanie danych
create/update), `process/sewing_tasks/`. Własne dataclass response w
`response.py` obok.

### 6.4 `core/repository/`

- **`psql/{domain}/{action}.py`** — jeden plik = jedna operacja DB (`create`,
  `one`, `collection`, `update`, `delete` + specjalizowane np.
  `stock_decrement`). Czyste zapytania SQLAlchemy, mapowanie ORM → dataclass w
  `response.py` danej domeny. Zawsze przez `managed_session(db_session)`.
  Dane wchodzą **już zwalidowane** — repository nie waliduje biznesowo.
- **`file/`** — repozytoria plikowe, np. `technical_pause/` (reader/writer
  JSON `maintenance.json`).

### 6.5 `core/tasks/` — Celery

Zadania asynchroniczne, pogrupowane domenowo (`auth/`, `payment/`, `order/`,
`b2b_application/`). Wzorzec:

```python
@celery_app.task(name="core.tasks.order.poll_inpost_delivery.poll_inpost_delivery_task")
def poll_inpost_delivery_task():
    ...
```

- Jawna, w pełni kwalifikowana nazwa taska w dekoratorze.
- Task otwiera **własną sesję** (`SessionLocal()`), nie dostaje jej z zewnątrz.
- Odporność przez logikę (błąd → `continue`, ponowienie w następnym przebiegu
  crona), nie przez auto-retry dekoratora.
- Harmonogram w `config/celery.py` (beat_schedule) — patrz sekcja 7.5.

### 6.6 `core/common/`

Wspólne narzędzia niskopoziomowe:

- `jwt.py` — encode/decode 3 typów tokenów (access `purpose="access"`,
  refresh `purpose="refresh"` + `family_id` do rotacji rodzin z
  reuse-detection, reset `purpose="password_reset"`); tuple pattern.
- `jwt_response.py` — dataclassy `AccessTokenResponse`,
  `RefreshTokenResponse`, `ResetTokenResponse`.
- `bcrypt_password.py` — `hash_password` / `verify_password`.
- `cart_token.py` — anonimowy token koszyka `{32-hex}.{hmac-sha256-hex}`,
  podpis HMAC z `cart_token_secret`, weryfikacja `hmac.compare_digest`.
- `http_retry.py` — `request_with_retry(...)` dla httpx: retry przejściowych
  5xx bram (502/503/504/520–524) z wykładniczym backoffem; dla
  `idempotent=False` NIE ponawia błędów niejednoznacznych (ReadTimeout), by
  uniknąć duplikatów.

### 6.7 `core/exceptions/` i `core/templates/`

- `exceptions/` — `AppException` + podklasy (sekcja 4.1) oraz
  `AtomicException` (nośnik `ApiErrorData` do rollbacku transakcji atomowych).
- `templates/emails/` — szablony HTML maili (welcome, order_confirmation,
  payment_failed, review_request, b2b_review).

---

## 7. Konfiguracja `config/`

### 7.1 `config/settings.py` — pydantic-settings + .env

Klasa `Settings(BaseSettings)`; singleton `settings = Settings()`. Czyta
`env/{ENV_MODE}.env` (tryb z env `WHERE_IS_WILLY_BACKEND_ENV_MODE`, domyślnie
`local`), przy czym **zmienne środowiskowe mają priorytet nad plikiem** (dzięki
temu CI ustawia env bez plików). Wszystkie pola mają alias z prefiksem
`WHERE_IS_WILLY_BACKEND_*` i walidatory (min_length na sekretach, zakresy
portów). Grupy: DB, JWT (TTL: access 15 min / refresh 30 dni / retention 60
dni), Redis, Stripe, InPost, Celery, Mail, Sentry, cache, dane bankowe,
cart token.

### 7.2 `config/app.py`

Cienki moduł: `ENV_MODE`, `BASE_DIR`, `ENV_PATH`. Skrypt
`infra/scripts/run_mode.sh {local|stg|prod}` podmienia `ENV_MODE` w tym pliku.

### 7.3 `config/redis.py` — cache

Synchroniczny klient `redis.Redis`. **Wartości serializowane JSON + kompresja
zlib.** Eksportuje: `get_cache_data`, `set_cache_data(key, value, timeout=300)`,
`delete_cache_key`, `delete_cache_by_prefix` (SCAN po kursorze),
`is_blacklisted` / `add_to_blacklist` (SETEX). Globalny wyłącznik
`CACHING_ENABLED` z settings. **Import modułu nawiązuje połączenie** (ping).

Wzorzec kluczy cache: `{domain}:{action}:{parametry}`, np.:

```
product:one:{product_id}
product:collection:{category_id}:{only_active}:{limit}:{offset}
product:variant:collection:{product_id}
auth_user:{user_id}
```

Redis pełni trzy role: cache danych (zlib), storage rate-limitera (slowapi)
oraz cache tożsamości/blacklisty (`auth_user:*`).

### 7.4 `config/rate_limit.py` — slowapi

`limiter = Limiter(key_func=get_remote_address, storage_uri=<redis>,
default_limits=["200/second"])` — storage w Redisie, więc limity współdzielone
między workerami gunicorna i replikami Swarm. Dodatkowo `auth_or_ip_key`
(limit per-user z JWT bez weryfikacji podpisu, fallback IP) oraz handler 429
zwracający standardowy envelope `ApiErrorResponse`.

### 7.5 `config/celery.py`

`celery_app = Celery("where_is_willy_backend", broker=..., backend=...)` —
broker **RabbitMQ**, backend **Redis** (URL-e z env). Serializacja json,
timezone `Europe/Warsaw`, jawna lista `include` z modułami tasków, import
wszystkich modeli ORM (kompletny rejestr mapperów workera).

**Beat schedule:**

| Task                    | Harmonogram              |
|-------------------------|--------------------------|
| `cancel-unpaid-orders`  | co 2 minuty              |
| `poll-inpost-delivery`  | 00:00 i 06:00            |
| `review-time-fallback`  | codziennie 03:00         |

### 7.6 `config/gunicorn.py`

Produkcyjny config: `bind 0.0.0.0:4444`, `workers=2`
(`uvicorn.workers.UvicornWorker`), `timeout=240`, `keepalive=65`,
`max_requests=1000` + jitter, `worker_tmp_dir=/dev/shm`, logi na
stdout/stderr, `forwarded_allow_ips="*"` (za reverse proxy). Start:
`gunicorn main:app -c config/gunicorn.py`.

### 7.7 `config/mail.py`, `config/metrics.py`, `config/sentry.py`

- **mail** — fastapi-mail `ConnectionConfig` z settings; `TEMPLATE_FOLDER` →
  `core/templates/emails`; eksport `fm = FastMail(conf)`.
- **metrics** — Prometheus (prometheus_client): `http_requests_total`,
  `http_request_duration_seconds`, `app_exceptions_total`,
  `api_error_responses_total`, `stripe_webhook_outcomes_total`. Label trasy to
  **szablon** (`/api/v1/products/{id}`), nie surowa ścieżka (kontrola
  cardinality). `init_metrics(app)` montuje `/metrics` (bez auth — chronione
  siecią) i `RequestLoggingMiddleware`.
- **sentry** — `init_sentry()` (integracje Starlette/FastAPI/SQLAlchemy,
  `send_default_pii=False`); `_before_send` dropuje oczekiwane `AppException`
  i szum health-checków; `ErrorObservabilityMiddleware` bumpuje metryki dla
  każdego error-envelope 4xx/5xx i wysyła do Sentry tylko realne bugi
  (≥500 + `key_type_error=="Exception"`), z fingerprintem
  `[type_module, type_error]`.

### 7.8 `config/swagger_description/`

Dokumentacja Swaggera trzymana w kodzie:

- `app.py` — `APP_DESCRIPTION` (markdown: envelope, ISO 8601, i18n, legenda ról),
- `summary.py` — `build_endpoint_summary(router)`: auto-generowana tabelka
  „ile endpointów per tag", liczona przy starcie,
- `tags.py` — `TAGS_METADATA`: ~24 tagi z opisami flow (auth, koszyk gościa,
  merge koszyka, InPost…).

---

## 8. `main.py` — złożenie aplikacji

Kolejność montażu (istotna):

1. `init_sentry()` — przed utworzeniem `app`.
2. `app = FastAPI(title=..., description=build_endpoint_summary(api_router) + APP_DESCRIPTION, openapi_tags=TAGS_METADATA, docs_url="/docs", redoc_url="/redoc")`.
3. Rate limiting: `app.state.limiter = limiter` + handler 429 + `SlowAPIMiddleware`.
4. CORS (`localhost:3000`, `localhost:5173`; nagłówki m.in. `X-Cart-Token`).
5. `add_error_observability_middleware(app, ...)`.
6. `register_exception_handlers(app)`.
7. `app.include_router(api_router)`.
8. `init_metrics(app)` — `/metrics` + logging middleware.
9. Static files: `app.mount("/static", StaticFiles(directory="static"))`
   (katalogi `static/categories`, `static/products` tworzone przy starcie).

Brak `lifespan` — połączenia (Redis, Sentry) inicjalizowane przez importy.
`runners/main.py` to osobny skrypt narzędziowy (generowanie hasha bcrypt do
seedowania admina).

---

## 9. Baza danych `database/psql/` + Alembic

### 9.1 Sesje i transakcje — `database/psql/database.py`

- Engine: `pool_size=3, max_overflow=2, pool_recycle=1800, pool_pre_ping=True`.
- **`get_db()`** — FastAPI dependency: yield sesji, **commit na sukces**,
  rollback + re-raise na wyjątek, close w finally.
- **`managed_session(db_session=None)`** — kluczowy context manager warstwy
  repository: jeśli sesja przyszła z endpointu (`Depends(get_db)`) → reużywa
  jej (commit robi endpoint/get_db); jeśli `None` (test standalone, task
  Celery) → tworzy własną i sam commituje. Dzięki temu każda funkcja `_psql`
  działa i samodzielnie, i w ramach większej transakcji.

### 9.2 Modele

`database/psql/models/{domain}.py` — SQLAlchemy 2.0 z `Mapped[]`, UUID PK,
JSONB dla pól i18n (`{"pl": ..., "en": ...}`) i multi-currency. Wspólna
`Base` w `base.py`.

### 9.3 Alembic — główna migracja tabel

**Alembic jest źródłem prawdy o schemacie.** Aktywny setup: katalog
`alembic/` + `alembic.ini`; `alembic/env.py` buduje URL przez `URL.create`
z `config.settings`, importuje pakiet `database.psql.models` (rejestracja
metadanych) i włącza `compare_type=True` / `compare_server_default=True` dla
autogenerate. Migracje numerowane: `0001_baseline` … `0010_product_reviews`.

### 9.4 Skrypty migracji — `infra/scripts/database/`

Wszystkie przyjmują argument środowiska `[local|stg|prod]`, ładują
`env/<env>.env`, walidują zmienne DB i testują połączenie `psql "SELECT 1"`:

- **`migration_up.sh`** — wykonuje `database/psql/sql/database_up.sql`
  (rozszerzenia `uuid-ossp`, `pgcrypto`, UTF8), potem
  `uv run alembic upgrade head`.
- **`migration_down.sh`** — destrukcyjny: `database_down.sql`
  (DROP ~34 tabel + ~25 typów enum CASCADE, czyści `alembic_version`).
- **`restart.sh`** — pełny reset schematu (downgrade base → drop → usunięcie
  plików wersji → `alembic revision --autogenerate` → migration_up).

Lokalnie wywoływane przez `make migration_up / migration_down /
migration_restart` (ENV=local domyślnie).

---

## 10. Testy `tests/` + pytest.ini

### 10.1 Struktura — lustrzane odbicie kodu

```
tests/
├── conftest.py                          ← fixtures globalne (testowa baza)
├── api/
│   ├── endpoints/{scope}/{domain}/      ← testy HTTP przez TestClient
│   │   ├── test_api_{action}.py
│   │   └── helper.py                    ← make_client, auth_header
│   └── middleware/                      ← testy JWT/CartIdentity middleware
├── config/                              ← testy redis, rate_limit, sentry, logging
├── core/
│   ├── common/                          ← testy jwt, bcrypt, cart_token, http_retry
│   ├── handler/{domain}/
│   ├── process/{domain}/
│   ├── repository/psql/{domain}/        ← testy jednostkowe _psql
│   │   ├── test_{action}.py
│   │   └── helper.py                    ← fabryki create_test_* / make_*
│   ├── service/{domain}/
│   └── tasks/{domain}/
└── files_for_tests/                     ← pliki testowe (obrazy itp.)
```

Każda warstwa kodu ma odpowiadający jej katalog testów — testy `_psql`
osobno, handlerów osobno, serwisów osobno, endpointów (HTTP) osobno.

### 10.2 pytest.ini (autorytatywny config)

- `testpaths = tests`, `pythonpath = .`, `asyncio_mode = auto`.
- **`addopts = -m "not slow and not integration and not full_integration and not api_integration"`**
  — ciężkie markery domyślnie WYKLUCZONE.
- Markery:
  - `slow` — testy stress/wyczerpujące,
  - `integration` — realna baza + realny Redis,
  - `full_integration` — pełna zewnętrzna integracja (sandbox InPost, etykiety),
  - `api_integration` — strzały do zewnętrznych API (Sentry ingest, InPost health).

**UWAGA:** przez `addopts` testy oznaczone `@pytest.mark.integration` są
domyślnie POMIJANE — nie dodawaj tego markera do testów `_psql`, które mają
się uruchamiać w standardowym przebiegu. CI uruchamia
`make run_test_integration` (filtr `not slow and not full_integration and not
api_integration` — czyli WŁĄCZA testy z DB/Redis, wyłącza tylko zewnętrzne API).

### 10.3 Testowa baza danych — `tests/conftest.py`

- **Realny lokalny Postgres** (nie sqlite, nie testcontainers). Fixture
  `test_engine` (scope session, autouse): łączy się do bazy `postgres` w
  AUTOCOMMIT, robi `DROP/CREATE DATABASE {db_name}_test`, włącza `pgcrypto`,
  tworzy schemat przez `Base.metadata.create_all` (nie przez alembic).
- **`db_session`** (scope function) — zwykła sesja sessionmaker.
- **Izolacja testów: `clean_tables`** (autouse) — po każdym teście
  `TRUNCATE TABLE ... CASCADE` wszystkich tabel (nie rollback/savepoint).

### 10.4 Wzorce testów

**Wszystkie testy piszemy jako klasy** — `class Test{Action}{Domain}Psql:` dla
`_psql`, `class TestApi{Scope}{Action}{Domain}:` dla endpointów. Metody wg
konwencji `test_{action}{nn:02d}_{opis}` (np. `test_create01_returns_ok`).
Żadnych luźnych funkcji testowych na poziomie modułu.

Test `_psql`:

```python
class TestCreateProductPsql:
    def test_create01_returns_ok(self, db_session: Session):
        result, err, ok = create_product_psql(..., db_session=db_session)
        assert ok is True and err is None and result.id is not None

    def test_create02_duplicate_slug_returns_integrity_error(self, db_session):
        make_product(db_session, slug="existing")
        _, err, ok = create_product_psql(slug="existing", ..., db_session=db_session)
        assert ok is False and err.key_type_error == "IntegrityError"
```

Test HTTP: helper `make_client(db_session, *routers)` tworzy świeży
`FastAPI()`, rejestruje exception handlery, nadpisuje `get_db` na testową
sesję i **montuje tylko routery potrzebne w teście** (nie całą aplikację).
Auth w teście: `create_test_user(role=ADMIN)` → `create_token_psql(user.id)`
→ nagłówek `Authorization: Bearer {access_token}`. Redis w testach
integracyjnych jest realny — sprzątanie cache ręcznie w `finally`
(`delete_cache_key`, `delete_cache_by_prefix`); alternatywnie w testach
middleware Redis mockowany przez `patch("api.middleware.Authentication.get_cache_data", ...)`.

Fabryki w `helper.py`: `create_test_*` tworzą encje wprost przez ORM z losowym
sufiksem `uuid4().hex[:8]`, `db.add` + `db.flush()` (bez commit), keyword-only
args z sensownymi defaultami.

---

## 11. CI/CD — GitHub Actions `.github/workflows/`

Sześć workflow w dwóch ścieżkach. Dwa **orkiestratory** (triggery `push`)
wywołują **workflow reużywalne** (`workflow_call`):

```
branch ≠ main:  run_test_local.yml ──► run_ci_test_local.yml (testy na runnerze)

main:           run_production.yml ──► run_ci_test_containers.yml   (smoke Swarm)
                                   └─► run_ci_production.yml         (build+push Docker Hub)
                                   └─► run_cd_production.yml         (deploy Ansible)
                                   └─► report (podsumowanie, if: always())
```

Każdy etap **gejtuje** następny przez `needs` — jeśli smoke padnie, obraz nie
trafi na Docker Hub; jeśli build padnie, nie ma deployu.

### 11.1 `run_test_local.yml` → `run_ci_test_local.yml` (testy)

- Trigger: push na **każdym branchu poza `main`** (main był już przetestowany
  przed merge) + `workflow_dispatch`.
- Job `tests` na `ubuntu-latest` z **services**: `postgres:16`
  (test_user/test_db, healthcheck `pg_isready`) i `redis:7-alpine`.
- Env ustawiany wprost na jobie (prefiks `WHERE_IS_WILLY_BACKEND_`,
  `ENV_MODE=ci`, wartości nie-sekretne) — settings czyta env priorytetowo,
  więc pliki `env/*.env` (gitignored) nie są potrzebne.
- Kroki: checkout → **`astral-sh/setup-uv@v5`** (z cache) →
  `uv python install 3.13` + `uv sync --all-extras` →
  **`make run_test_integration`**.

### 11.2 `run_ci_test_containers.yml` — Container Smoke (single-node Swarm)

Jeden krok: `bash infra/scripts/ci/ci_smoke.sh`. Trzywarstwowy smoke całego
stacku PRZED buildem produkcyjnym:

1. **Layer 1 — import/mappery**: build obrazu produkcyjnego, `docker run`
   z `python -c "import config.celery; import database.psql.models;
   configure_mappers()"` — łapie `ModuleNotFoundError` / błędy mapperów.
2. **Layer 2 — deploy stacku**: `docker swarm init` na runnerze, sieci
   overlay, docker secret z `env/ci_test.env.example`,
   `docker stack deploy -c production.swarm.docker-compose.yaml -c
   ci_test.swarm.override.yaml` (override dodaje kontener `postgres:17-alpine`
   i redukuje backend do 1 repliki). Czeka na konwergencję replik
   (3 kolejne zgodne odczyty) + skan logów po twardych błędach.
3. **Layer 3 — probes**: `curl /docs` na backendzie, test łańcucha
   backend→pgbouncer→postgres (`select 1` w kontenerze), `celery inspect ping`
   workera.

### 11.3 `run_ci_production.yml` — build + push (Docker Hub)

- Sekrety: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `REPOSITORY`; environment `stg`.
- Wersja obrazu = timestamp `YYYYMMDDHHMM`; build z
  `infra/dockerfiles/dockerfile/production.dockerfile`; push tagów
  `:{timestamp}` i `:latest`.

### 11.4 `run_cd_production.yml` — deploy (Ansible)

- Sekrety: `SSH_PRIVATE_KEY`, `ANSIBLE_PASSWORD` (vault), `TARGET_HOST`, `SSH_USER`.
- Kroki: `pip install ansible-core>=2.16` → setup klucza SSH + known_hosts →
  render `inventory.ini` (sed podmienia placeholdery hosta/usera) →
  `ansible-playbook -i inventory.ini playbook_deploy.yml --vault-password-file ...`
  → cleanup sekretów z runnera (`if: always()`).

### 11.5 Pozostałe skrypty `infra/scripts/`

- `run_tests.sh {local|stg|prod}` — Layer 1 import-check + `uv run --extra test pytest`.
- `run_mode.sh {local|stg|prod}` — przełącza `ENV_MODE` w `config/app.py` (sed).
- `docker_entrypoint.sh` — entrypoint dev: naprawa CRLF, migracje
  (`migration_up.sh local`), `uvicorn --reload`.
- `load_env.sh` — source odpowiedniego `env/*.env` z walidacją zmiennych DB.
- `vault.sh {decrypt|encrypt|view}` — ansible-vault w jednorazowym kontenerze
  (obraz z `vault.dockerfile`), hasło przez env `ANSIBLE_PASSWORD`.

### 11.6 Pull request template

`.github/pull_request_template.md`: Summary / Type of change / Checklist
(migracja DB? breaking API? testy? nowe env vars udokumentowane? testowane
lokalnie?) / Test plan / Notes for reviewer.

---

## 12. Infrastruktura `infra/`

### 12.1 Dockerfiles — `infra/dockerfiles/dockerfile/`

- **`production.dockerfile`** — `python:3.14-slim` + binarka **uv** kopiowana
  z `ghcr.io/astral-sh/uv:latest`. Instalacja: `uv sync --frozen --no-dev
  --extra prod` (tylko produkcyjne zależności z lockfile). CMD:
  `gunicorn main:app -c config/gunicorn.py`. Ten sam obraz służy jako API,
  Celery worker i Celery beat (różne komendy w compose).
- **`test.dockerfile`** — toolchain buildowy + `uv sync --frozen` (z dev),
  CMD `uv run pytest -v -s`.
- **`vault.dockerfile`** — `pip install ansible-core` — tylko `ansible-vault`
  do (de)szyfrowania `secrets.yml`.

### 12.2 Development lokalny — `compose/local.docker-compose.yaml`

Minimalny stack: **tylko `dev_rabbitmq`** (`rabbitmq:3-management`, porty
5672 + 15672 UI) i **`dev_redis`** (`redis:7`, port 6379). Backend, worker i
Postgres uruchamiane lokalnie poza composem (`make run_app`,
`make run_celery_worker`). Podnoszone przez `make docker_up`.

### 12.3 Produkcja — Docker Swarm (`compose/production.swarm.docker-compose.yaml`)

Deploy jako stack `whereiswilly`. Wszystkie serwisy montują **docker secret**
z bundlem env (`whereiswilly_env_prod_<hash>`) i źródłują go w entrypoint —
zero plików `.env` na dysku serwera. Serwisy:

| Serwis                  | Obraz                          | Rola                                    | Repliki | Port |
|-------------------------|--------------------------------|-----------------------------------------|---------|------|
| `whereiswilly_backend`  | obraz z Docker Hub             | API (gunicorn)                          | **2**   | 4444 |
| `whereiswilly_celery_worker` | ten sam obraz             | Celery worker (`--concurrency=3 --pool=threads -E`) | 1 | — |
| `whereiswilly_celery_beat`   | ten sam obraz             | scheduler Celery                        | 1       | —    |
| `whereiswilly_redis`    | `redis:7-alpine`               | cache + backend Celery (requirepass, LRU 256 MB) | 1 | — |
| `whereiswilly_rabbitmq` | `rabbitmq:3.13-management`     | broker AMQP                             | 1       | —    |
| `whereiswilly_pgbouncer`| bitnami pgbouncer              | pooler do natywnego Postgresa na hoście (transaction mode) | 1 | — |
| `whereiswilly_flower`   | `mher/flower`                  | monitoring Celery UI                    | 1       | 5555 |
| `whereiswilly_prometheus` | `prom/prometheus`            | metryki (retencja 15 dni)               | 1       | 9090 |
| `whereiswilly_grafana`  | `grafana/grafana`              | dashboardy (datasource auto-provisioning) | 1     | 3000 |
| exportery               | redis / celery / postgres exporter | metryki do Prometheusa              | 1 każdy | —   |

- **Postgres jest natywny na hoście** (nie w kontenerze) — aplikacja łączy się
  przez PgBouncer.
- Dwie sieci overlay external: `whereiswilly_backend_network_traefik`
  (gateway) i `whereiswilly_backend_production` (magistrala).
- **Traefik** (`traefik_production_stack.yaml`) — osobny stack
  `whereiswilly_traefik`: `traefik:v2.11`, entrypoints :80/:443,
  Let's Encrypt TLS challenge. (Na etapie staging routing przez Traefik
  wyłączony — serwisy wystawione na porty hosta.)
- Monitoring: Prometheus scrapuje backend (`tasks.whereiswilly_backend:4444/metrics`
  — DNS SD, bo 2 repliki), flower, rabbitmq, exportery.

### 12.4 Deploy — Ansible (`infra/ansible/`)

`playbook_deploy.yml` (uruchamiany z CD, `become: true`, sekrety infry w
zaszyfrowanym `secrets.yml` — ansible-vault). Model: **CI buduje i pushuje
obraz, CD tylko pulluje i deployuje**. Kolejność tasków:

1. **`checkout.yml`** — clone/refresh repo przez HTTPS + PAT (token usuwany
   z `.git/config` po checkout).
2. **`networks.yml`** — idempotentne utworzenie sieci overlay przed deployem.
3. **`secret_env.yml`** — pobiera sekrety z **Dopplera**, liczy hash sha256,
   tworzy **content-hashed docker secret** `whereiswilly_env_prod_v<hash>`
   (brak zmian w Dopplerze → ta sama nazwa → Swarm nic nie restartuje);
   sprząta stare wersje.
4. **`deploy.yml`** — `docker login` → `docker stack deploy` Traefika →
   `docker stack deploy --with-registry-auth` stacku głównego (z env
   `WHERE_IS_WILLY_ENV_SECRET_VERSION` i `BACKEND_IMAGE`).
5. **`rabbitmq_provision.yml`** — czeka aż RabbitMQ wstanie, idempotentnie
   tworzy usera aplikacji + uprawnienia.
6. **`cleanup.yml`** — `docker image prune -f`.

Sekrety aplikacji żyją w **Dopplerze** (projekt per backend, config per
środowisko); sekrety infrastrukturalne (token Dopplera, PAT, docker hub) w
`secrets.yml` szyfrowanym ansible-vault (obsługa przez `make vault_*`).

---

## 13. Zmienne środowiskowe `env/`

Pliki `env/{local|stg|prod}.env` (gitignored; w repo `ci_test.env.example`).
Wszystkie zmienne z prefiksem **`WHERE_IS_WILLY_BACKEND_`**, czytane przez
`config/settings.py` (env ma priorytet nad plikiem). Grupy:

| Grupa       | Zmienne (bez prefiksu)                                                       |
|-------------|-------------------------------------------------------------------------------|
| Środowisko  | `ENV_MODE`, `CACHING_ENABLED`                                                 |
| Baza        | `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_DBNAME`, `PGBOUNCER_DB_HOST` |
| Redis       | `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`                                  |
| Celery/AMQP | `CELERY_BROKER`, `CELERY_BACKEND`, `RABBIT_PASSWORD`                          |
| JWT         | `TOKEN_KEY`, `TOKEN_ALGORITHM`, `ACCESS_TOKEN_TTL_MINUTES`, `REFRESH_TOKEN_TTL_DAYS`, `REFRESH_TOKEN_RETENTION_DAYS` |
| Koszyk      | `TOKEN_X_CART` (min 32 znaki)                                                 |
| Mail        | `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_PORT`, `MAIL_SERVER`, `MAIL_FROM_NAME`, `MAIL_STARTTLS`, `MAIL_SSL_TLS` |
| Stripe      | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL` |
| InPost      | `INPOST_API_TOKEN`, `INPOST_ORGANIZATION_ID`, `INPOST_API_URL`, `INPOST_WEBHOOK` |
| Bank        | `BANK_ACCOUNT_HOLDER`, `BANK_NAME`, `BANK_IBAN`, `BANK_SWIFT`, `BANK_TRANSFER_INSTRUCTIONS` |
| Sentry      | `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, `SENTRY_PROFILES_SAMPLE_RATE`, `SENTRY_RELEASE`, `SENTRY_ENVIRONMENT` |
| Monitoring  | `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, `FLOWER_USER`, `FLOWER_PASSWORD` |

Format bundla sekretów (Doppler → docker secret): płaski `KEY=val`, bez
cudzysłowów, żaden klucz wieloliniowy.

---

## 14. Konwencje nazewnictwa

| Element               | Wzorzec                          | Przykład                     |
|-----------------------|----------------------------------|------------------------------|
| funkcja `_psql`       | `{action}_{domain}_psql`         | `create_product_psql`        |
| funkcja handlera      | `handler_{action}_{domain}`      | `handler_create_product`     |
| funkcja endpointu     | `api_{scope}_{action}_{domain}`  | `api_admin_create_product`   |
| plik endpointu        | `{action}.py`                    | `create.py`, `collection.py` |
| stała URL             | `{SCOPE}_{DOMAIN}_{ACTION}`      | `ADMIN_PRODUCTS_CREATE`      |
| klucz cache           | `{domain}:{action}:{params}`     | `product:one:{id}`           |
| klasa testowa         | `Test{Action}{Domain}Psql`       | `TestCreateProductPsql`      |
| metoda testowa        | `test_{action}{nn:02d}_{opis}`   | `test_create01_returns_ok`   |
| `type_module` w error | nazwa funkcji, gdzie rzucony     | `"create_product_psql"`      |
| nazwa taska Celery    | pełna ścieżka modułu + nazwa     | `core.tasks.order.poll_inpost_delivery.poll_inpost_delivery_task` |

---

## 15. Checklista: dodawanie nowej funkcjonalności

1. **Model** — `database/psql/models/{domain}.py` + migracja Alembic.
2. **_psql response** — `core/repository/psql/{domain}/response.py`
   (dataclass + `_to_*_response`).
3. **_psql operacje** — `core/repository/psql/{domain}/{action}.py`
   (tuple pattern, `managed_session`).
4. **Handler** — `core/handler/{domain}/{action}.py` (tuple pattern +
   cache/invalidacja). Jeśli logika wielotabelowa / zewnętrzne API → dodatkowo
   `core/service/{domain}/`; przetwarzanie danych → `core/process/{domain}/`.
5. **Schemas** — `api/schemas/{domain}/` (Payload + ResponseData, walidatory i18n).
6. **URL** — stała w `api/endpoints/urls.py`.
7. **Endpoint** — `api/endpoints/{scope}/{domain}/{action}.py`
   (swagger obowiązkowy: summary z rolą, responses, tags).
8. **Router** — rejestracja w `api/router.py` (własna sekcja z komentarzem).
9. **Testy** — `tests/core/repository/psql/{domain}/test_{action}.py` +
   `tests/api/endpoints/{scope}/{domain}/test_api_{action}.py` (+ helper.py
   z fabrykami).
10. Jeśli nowe zmienne env → dodać do `env/*.env` i `config/settings.py`
    (+ udokumentować w PR).

---

## 16. Znane rozbieżności / uwagi porządkowe

Wykryte podczas analizy — warto wyprostować przy okazji refaktoryzacji:

1. **Dwa równoległe katalogi migracji**: aktywny `alembic/` (10 migracji,
   `URL.create`, `compare_type=True`) oraz starszy
   `database/psql/migrations/` (pojedynczy init) — `alembic.ini` w polu
   `script_location` wskazuje na ten starszy, ale README i praktyka używają
   `alembic/`. Docelowo zostawić jeden.
2. **README vs Makefile**: README wspomina targety `make migrate*`, które nie
   istnieją — faktyczne to `migration_up/down/restart`.
3. **README vs conftest**: README opisuje izolację testów przez
   savepoint/rollback — faktycznie jest `TRUNCATE ... CASCADE` po każdym
   teście; prefiks env to `WHERE_IS_WILLY_BACKEND_`, nie `WHEREISWILLY_BACKEND_`.
4. **`load_env.sh`** akceptuje `dev` zamiast `stg` (inne skrypty używają `stg`)
   — ujednolicić nazwy środowisk.
5. **Python w obrazach vs CI**: dockerfile bazuje na `python:3.14-slim`,
   CI instaluje 3.13, pyproject dopuszcza `>=3.13,<3.15` — spójne, ale warto
   świadomie przypiąć jedną wersję.
6. **`env/local.env` w repo zawiera realne sekrety** (InPost sandbox JWT,
   Sentry DSN, hasła) — powinny zostać zrotowane i plik usunięty z historii
   (docelowo tylko `*.env.example` w repo).
7. Dwa wzorce błędów współistnieją (tuple pattern + `AppException`) — nowy kod
   endpointów pisać spójnie z resztą domeny; docelowa migracja na wyjątki
   opisana w README (kontrakt envelope pozostaje ten sam).
