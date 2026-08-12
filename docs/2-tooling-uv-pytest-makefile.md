# 2 — Tooling: `pyproject.toml`, `uv`, `pytest`, `Makefile`

## Kontekst

Obecny projekt nie ma żadnego pliku deklarującego zależności (brak
`requirements.txt`, brak `pyproject.toml`) — zależności (`fastapi`,
`sqlalchemy`, `python-decouple`, `pyjwt`, `passlib[bcrypt]`, ...) trzeba
odtworzyć z importów w kodzie. To zadanie jest fundamentem pod pkt. 3 — bez
tego nie odpalimy testów ani nowej struktury.

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 2 (uv + Makefile).

## Kroki

- [ ] `pyproject.toml` — nazwa pakietu, `build-system` (setuptools), lista
      zależności głównych odtworzona z obecnych importów
- [ ] Grupy opcjonalne (`extras`): `test` (pytest, pytest-cov, pytest-mock,
      httpx dla TestClient), `dev` (ruff, pre-commit)
- [ ] `uv.lock` — `uv sync --all-extras`
- [ ] `ruff` config w `pyproject.toml` (line-length, target-version, reguły)
- [ ] `.pre-commit-config.yaml` (trailing-whitespace, ruff, ruff-format, itp.)
- [ ] `pytest.ini` — `testpaths`, `pythonpath`, markery (`slow`,
      `integration` jeśli będzie potrzebne)
- [ ] `Makefile` — targety zaadaptowane do skali tego projektu:
      `install`, `run_app`, `run_test`, `clean` (bez Celery/InPost — to nie
      dotyczy tego projektu, przenosimy tylko sensowną podstawę)
- [ ] `.gitignore` uzupełnić (obecnie **pusty plik** — `.env` jest realnie
      commitowany do repo, patrz uwaga niżej)
- [ ] `.env.example` zamiast realnego `.env` w repo

## Ważna uwaga bezpieczeństwa (do zaadresowania w tym zadaniu)

`.env` jest śledzony przez git od pierwszego commita (`0696a2b`). Sekrety w
nim (jeśli realne, nie placeholdery) powinny zostać **zrotowane**, a plik
usunięty z trackingu (`git rm --cached .env`) i dodany do `.gitignore`.
Wyczyszczenie z historii gita to osobna decyzja (rewrite historii) — do
ustalenia z Tobą przed wykonaniem, bo to operacja destrukcyjna na repo.

## Do potwierdzenia z Tobą przed startem

- Czy projekt ma zostać na FastAPI sync (obecny styl) czy przechodzimy na
  async SQLAlchemy 2.0 zgodnie z wzorcem referencyjnym?
- Docelowa wersja Pythona?
