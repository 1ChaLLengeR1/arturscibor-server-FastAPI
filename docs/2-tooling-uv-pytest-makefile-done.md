# 2 — Tooling: `pyproject.toml`, `uv`, `pytest`, `Makefile`

## Kontekst

Obecny projekt nie miał żadnego pliku deklarującego zależności (brak
`requirements.txt`, brak `pyproject.toml`) — zależności (`fastapi`,
`sqlalchemy`, `python-decouple`, `pyjwt`, `passlib[bcrypt]`, ...) odtworzone
z importów w kodzie. To zadanie jest fundamentem pod pkt. 3 — bez tego nie
odpalimy testów ani nowej struktury.

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 2 (uv + Makefile).

## Kroki

- [x] `pyproject.toml` — nazwa pakietu, `build-system` (setuptools), lista
      zależności głównych odtworzona z obecnych importów (w tym
      `python-multipart`, wymagane przez `Form()`/`UploadFile`, którego
      wcześniej nigdzie nie deklarowano)
- [x] Grupy opcjonalne (`extras`): `test` (pytest, pytest-cov, pytest-mock,
      httpx dla TestClient), `dev` (ruff) — **bez pre-commit**, na wyraźną
      prośbę: pre-commit spowalnia commit, więc go pomijamy w tym projekcie
- [x] `uv.lock` — wygenerowany przez `uv sync --all-extras`, zweryfikowane
      że `uv run pytest` i `uv run ruff check` odpalają się poprawnie
- [x] `ruff` config w `pyproject.toml` (line-length=120, target-version=py312,
      reguły E,F,W,I,N,UP,B,SIM, ignore B008) — pierwszy przebieg na starym
      kodzie zgłasza 73 błędy (spodziewane, stary kod nie był lintowany;
      sprzątanie stylu odbędzie się przy migracji każdej sekcji w pkt. 3, nie
      teraz hurtem)
- [x] `pytest.ini` — `testpaths=tests`, `pythonpath=.`; bez markerów
      (`slow`/`integration`) — nie ma jeszcze żadnych testów które by ich
      potrzebowały, dodamy gdy realnie będą potrzebne (pkt. 3)
- [x] `Makefile` — targety `install`, `run_app`, `run_test`, `clean` (bez
      Celery/InPost — to nie dotyczy tego projektu)
- [x] `.gitignore` uzupełniony (był **pusty plik** — `.env` był realnie
      commitowany do repo, patrz sekcja bezpieczeństwa niżej)
- [x] `env/local.env` + `env/example-local.env` zamiast realnego `.env` w
      repo (patrz niżej)

## Bezpieczeństwo — `.env`

`.env` był śledzony przez git od pierwszego commita (`0696a2b`). Po
sprawdzeniu zawartości: **wszystkie wartości były puste** (placeholdery,
żadnych realnych sekretów) — nic do rotacji. Mimo to:

- [x] Usunięty z trackingu (`git rm --cached .env`) i z dysku
- [x] Zastąpiony strukturą `env/`:
  - `env/example-local.env` — commitowany, same klucze z pustymi/przykładowymi
    wartościami, punkt odniesienia co w ogóle trzeba ustawić
  - `env/local.env` — **gitignored**, realne wartości do developmentu
    lokalnego (wygenerowane losowe `SECRET_ADMIN_TOKEN`/`REFRESH_ADMIN_TOKEN`
    przez `secrets.token_hex(32)`, żeby środowisko dev działało od razu "out
    of the box")
- [x] Wyczyszczenie z **historii** gita (rewrite historii) świadomie
  pominięte — realnie nic wrażliwego tam nie było (same puste placeholdery),
  więc nie ma powodu do destrukcyjnej operacji na historii repo

## Ważna uwaga — wiązanie configu z `env/` to dopiero pkt. 3

`python-decouple` (`from decouple import config`), którego obecnie używa
kod (`JWT/jwt_helper.py`, `routers/authentication/*`, `routers/Projects/*`,
`routers/Contact/*`), domyślnie szuka pliku `.env` w bieżącym katalogu
roboczym w górę drzewa katalogów — **nie zajrzy samo do `env/local.env`**.
Realne wpięcie configu (`config/settings.py` z `pydantic-settings`, czytanie
`env/{ENV_MODE}.env`) to zadanie z pkt. 3 (`3-layered-architecture.md`), nie
tego kroku. Do tego czasu `env/local.env` służy jako gotowy, poprawny zestaw
wartości czekający na podłączenie — aplikacja i tak obecnie nie odpala się
(patrz `DataBase/db.py` — `Data_Base_Url` jest pustym przypisaniem, błąd
składni), więc nie psujemy niczego, co wcześniej działało.

## Rozstrzygnięte decyzje

- **Sync vs async SQLAlchemy 2.0**: zostajemy na sync na razie — zależności
  odzwierciedlają obecny (sync) styl kodu. Przejście na async to decyzja do
  podjęcia świadomie w pkt. 3 przy przepisywaniu `database/psql/database.py`,
  nie coś do wymuszania już na etapie samego toolingu.
- **Wersja Pythona**: `requires-python = ">=3.12"` w `pyproject.toml`
  (środowisko ma dostępne `uv` + Python 3.13/3.14 — `uv` samo dobiera
  odpowiedni interpreter przy `uv sync`).

## Status

Ukończone.
