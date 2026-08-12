# 3 — Szkielet warstwowy `api/` `core/` `database/` `config/`

## Kontekst

Zakładamy docelową strukturę katalogów wg `docs/ARCHITEKTURA.md` (sekcja 3-4),
w skali dopasowanej do tego projektu (bez Celery/Redis/Stripe/InPost — to nie
dotyczy portfolio). `core/` uproszczone względem wzorca referencyjnego — bez
`process/`, `exceptions/`, `templates/` — tylko: `handler`, `repository`,
`service`, `tasks`, `template`, `utils`, `common`. Migracja domen odbywa się
sekcja po sekcji — patrz podzadania `3.x`.

## Utworzony szkielet

```
api/
├── endpoints/            (puste — pierwsze pliki dodaje 3.1)
├── middleware/           (puste — JWTAuthenticationMiddleware dodaje 3.1)
├── schemas/               (puste — per-domena w 3.1-3.5)
├── router.py              ← api_router = APIRouter(), domeny się do niego rejestrują
├── response.py             ← ApiResponse / ApiErrorData / ApiErrorResponse (PEP 695 generics)
└── exception_handlers.py   ← register_exception_handlers(app), fallback 500 na Exception
core/
├── handler/                (puste — per-domena)
├── repository/              (puste — per-domena)
├── service/                 (puste — per-domena)
├── tasks/                   (puste — per-domena, jeśli w ogóle będzie potrzebne)
├── template/                (puste — jeśli/gdy pojawi się mail/PDF itp.)
├── utils/                   (puste)
└── common/
    ├── jwt.py                ← create/decode access+refresh token (parametryzowane przez settings)
    └── bcrypt_password.py    ← hash_password/verify_password (bezpośrednio na `bcrypt`, nie passlib)
config/
├── app.py                 ← ENV_MODE, BASE_DIR, ENV_PATH (env/{ENV_MODE}.env)
└── settings.py             ← Settings(BaseSettings) — pydantic-settings
database/psql/
├── base.py                 ← Base(DeclarativeBase)
├── database.py              ← engine, get_db() (sesja per-request!), managed_session()
└── models/                  (puste — modele dopisywane per-domena w 3.1-3.5)
```

## Kroki

- [x] Utworzyć puste pakiety (`__init__.py`) wg szkieletu powyżej
- [x] `config/settings.py` (pydantic-settings) — czyta `env/{ENV_MODE}.env`
      (domyślnie `local` → `env/local.env`); `python-decouple` **zostaje na
      razie jako zależność** — stary `routers/`/`JWT/` nadal go używa, znika
      dopiero jak te pliki zostaną zastąpione w 3.1-3.5
- [x] `database/psql/database.py` — `get_db()` (per-request session!) +
      `managed_session()` — **naprawia realny bug**: stary `db =
      SessionLocal()` w `DataBase/db.py` tworzył jedną globalną, współdzieloną
      sesję na cały proces (brak izolacji między requestami)
- [x] `api/response.py`, `api/exception_handlers.py` — **wybrany tuple
      pattern, bez hierarchii `AppException`** (stąd brak `core/exceptions/`
      w uproszczonej strukturze — jeden spójny wzorzec błędów zamiast dwóch
      współistniejących jak w projekcie referencyjnym)
- [x] `core/common/jwt.py` — jeden spójny, niskopoziomowy mechanizm
      encode/decode (naprawiony też `jwt.decode(..., algorithms=[...])` jako
      lista — stary kod przekazywał pojedynczy string pozycyjnie).
      **Podłączenie go do faktycznego flow logowania (żeby zwykli userzy
      dostawali prawdziwy JWT, nie `secrets.token_hex()`) to zadanie 3.1**,
      nie tego kroku — to wymaga przepisania też modelu `Users` i endpointu
      `/authentication/login`.
- [ ] `database/psql/models/` — **przeniesione do 3.1-3.5**: modele
      przepisywane na SQLAlchemy 2.0 `Mapped[]` per-domena, w miarę migracji
      każdej sekcji (nie hurtem teraz, bo i tak trzeba to robić z testami per
      domena)
- [ ] Alembic — **przeniesione do 3.1** (pierwszej sekcji): sensowna pierwsza
      migracja wymaga chociaż jednego realnego modelu, których tu jeszcze nie
      ma

## Znaleziony po drodze problem (naprawiony)

`passlib[bcrypt]` (używane w starym `routers/authentication/utilities.py`)
jest niekompatybilne z nowszymi wersjami paczki `bcrypt` (passlib nie jest
już aktywnie utrzymywane — `AttributeError: module 'bcrypt' has no attribute
'__about__'`, potem błąd przy realnym hashowaniu). `core/common/bcrypt_password.py`
używa bezpośrednio `bcrypt` (zgodnie z `ARCHITEKTURA.md`, sekcja 1: "Hasła:
bcrypt", nie passlib) — działa poprawnie, zweryfikowane round-tripem hash/verify.
Stary plik `routers/authentication/utilities.py` zostanie zastąpiony w 3.1,
ale warto wiedzieć, że jego obecna wersja i tak już nie działa z powodu tej
niezgodności wersji.

## Weryfikacja

- `uv run python -c "..."` — import + smoke-test wszystkich nowych modułów
  (`config.settings`, `database.psql.database`, `core.common.jwt`,
  `core.common.bcrypt_password`, `api.response`, `api.exception_handlers`,
  `api.router`) — działa
- `uv run ruff check api/ core/ database/ config/` — czysto
- `uv run pytest` — nadal 0 testów (bez zmian, testy dochodzą per-domena w 3.1-3.5)

## Zależność

Wymagało ukończenia [2 — tooling](2-tooling-uv-pytest-makefile-done.md).

## Podzadania (sekcje z `routers/` → `api/endpoints/`)

- [ ] [3.1 — authentication](3.1-auth-section.md)
- [ ] [3.2 — contact](3.2-contact-section.md)
- [ ] [3.3 — tools](3.3-tools-section.md)
- [ ] [3.4 — aboutme + home](3.4-aboutme-home-section.md)
- [ ] [3.5 — projects](3.5-projects-section.md)

## Status

Szkielet ukończony. Podzadania `3.x` (per-domena) zostają otwarte — to
osobne taski.
