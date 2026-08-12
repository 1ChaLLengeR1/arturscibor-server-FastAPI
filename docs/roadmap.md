# Roadmapa refaktoru → architektura docelowa (`docs/ARCHITEKTURA.md`)

> Ten plik jest tylko indeksem. Każde zadanie ma swój plik `N-nazwa.md` (albo
> `N.x-nazwa.md` dla podzadań sekcji z pkt. 3). Odznaczamy checkboxy w miarę
> postępu, dopisujemy nowe `3.x` w miarę odkrywania kolejnych sekcji.

## Zadania główne

- [x] [1 — Branch master → main](1-branch-main-done.md)
- [ ] [2 — Tooling: pyproject.toml, uv, pytest, Makefile](2-tooling-uv-pytest-makefile.md)
- [ ] [3 — Szkielet warstwowy api/ core/ database/ config/](3-layered-architecture.md)
  - [ ] [3.1 — Sekcja: authentication](3.1-auth-section.md)
  - [ ] [3.2 — Sekcja: contact](3.2-contact-section.md)
  - [ ] [3.3 — Sekcja: tools](3.3-tools-section.md)
  - [ ] [3.4 — Sekcje: aboutme + home (scalenie duplikatu)](3.4-aboutme-home-section.md)
  - [ ] [3.5 — Sekcja: projects](3.5-projects-section.md)
- [ ] [4 — Infra: ansible/ dockerfiles/ scripts/](4-infra.md)
- [ ] [5 — CI/CD (GitHub Actions)](5-ci-cd.md)

## Kolejność sekcji w pkt. 3 (od najprostszej do najbardziej złożonej)

1. `authentication` — fundament, wszystko inne wisi na JWT
2. `contact` — najmniejsza domena, dobry poligon pod wzorzec warstw
3. `tools` — prosty CRUD jednej tabeli
4. `aboutme` + `home` — trzeba najpierw rozstrzygnąć duplikat `upload-me`/`information-me`
5. `projects` — największa domena (sub-resource: images, technologies, download)

## Referencje

- Wzorzec docelowy: [`docs/ARCHITEKTURA.md`](ARCHITEKTURA.md)
- Stan wyjściowy (do skasowania po migracji): `JWT/`, `routers/`, `DataBase/`
