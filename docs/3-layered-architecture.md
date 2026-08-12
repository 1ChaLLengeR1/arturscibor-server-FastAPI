# 3 — Szkielet warstwowy `api/` `core/` `database/` `config/`

## Kontekst

Zakładamy docelową strukturę katalogów wg `docs/ARCHITEKTURA.md` (sekcja 3-4),
w skali dopasowanej do tego projektu (bez Celery/Redis/Stripe/InPost — to nie
dotyczy portfolio, chyba że zdecydujemy inaczej). Migracja odbywa się
sekcja po sekcji — patrz podzadania `3.x`.

## Docelowy szkielet (do utworzenia jako puste/`__init__.py`)

```
api/
├── endpoints/{domain}/{action}.py
│   └── urls.py
├── middleware/          ← JWTAuthenticationMiddleware
├── schemas/{domain}/
├── router.py
├── response.py          ← ApiResponse / ApiErrorResponse / ApiErrorData
├── exception_handlers.py
└── validators.py
core/
├── handler/{domain}/{action}.py
├── repository/psql/{domain}/{action}.py + response.py
├── common/               ← jwt.py, bcrypt_password.py
├── exceptions/
└── utils/
config/
├── settings.py           ← pydantic-settings
└── app.py
database/psql/
├── database.py           ← engine, get_db, managed_session
├── base.py
└── models/{domain}.py
```

## Kroki

- [ ] Utworzyć puste pakiety (`__init__.py`) wg szkieletu powyżej
- [ ] `config/settings.py` (pydantic-settings) — zastąpienie `python-decouple`
- [ ] `database/psql/database.py` — `get_db()` (per-request session!) +
      `managed_session()` — **naprawia realny bug**: obecny `db =
      SessionLocal()` w `DataBase/db.py` tworzy jedną globalną, współdzieloną
      sesję na cały proces (brak izolacji między requestami)
- [ ] `database/psql/models/` — przepisanie modeli na SQLAlchemy 2.0
      (`Mapped[]`), dodanie brakujących `ForeignKey` (obecnie relacje przez
      gołe stringi `id_project`/`id_message` bez FK)
- [ ] `api/response.py`, `api/exception_handlers.py` — envelope + tuple
      pattern albo `AppException` (do ustalenia który wzorzec bierzemy —
      projekt referencyjny ma oba współistniejące, ale dla nowego kodu warto
      wybrać jeden od razu)
- [ ] `core/common/jwt.py` — jeden spójny mechanizm JWT dla WSZYSTKICH
      użytkowników (obecnie zwykli userzy dostają losowy `secrets.token_hex()`
      zamiast JWT — do naprawienia)
- [ ] Alembic — `alembic/` + pierwsza migracja bazująca na obecnym schemacie

## Zależność

Wymaga ukończenia [2 — tooling](2-tooling-uv-pytest-makefile.md) (potrzebne
`pyproject.toml` + `uv` żeby cokolwiek odpalić/testować).

## Podzadania (sekcje z `routers/` → `api/endpoints/`)

- [ ] [3.1 — authentication](3.1-auth-section.md)
- [ ] [3.2 — contact](3.2-contact-section.md)
- [ ] [3.3 — tools](3.3-tools-section.md)
- [ ] [3.4 — aboutme + home](3.4-aboutme-home-section.md)
- [ ] [3.5 — projects](3.5-projects-section.md)
