# Roadmapa refaktoru → architektura docelowa (`docs/ARCHITEKTURA.md`)

> Ten plik jest tylko indeksem. Każde zadanie ma swój plik `N-nazwa.md` (albo
> `N.x-nazwa.md` dla podzadań sekcji z pkt. 3). Odznaczamy checkboxy w miarę
> postępu, dopisujemy nowe `3.x` w miarę odkrywania kolejnych sekcji.

## Zadania główne

- [x] [1 — Branch master → main](1-branch-main-done.md)
- [x] [2 — Tooling: pyproject.toml, uv, pytest, Makefile](2-tooling-uv-pytest-makefile-done.md)
- [x] [3 — Szkielet warstwowy api/ core/ database/ config/](3-layered-architecture-done.md)
  - [x] [3.1 — Sekcja: authentication](3.1-auth-section-done.md)
  - [x] [3.2 — Sekcja: contact](3.2-contact-section-done.md)
  - [x] [3.3 — Sekcja: tools](3.3-tools-section-done.md)
  - [x] [3.4 — Sekcje: aboutme + work + cv (markdown + karuzele, wzorem tools)](3.4-aboutme-home-section-done.md)
  - [ ] [3.5 — Sekcja: projects](3.5-projects-section.md)
- [x] [4 — Infra: ansible/ dockerfiles/ scripts/](4-infra-done.md)
- [ ] [5 — CI/CD (GitHub Actions)](5-ci-cd.md)
- [x] [6 — Sekcja: file (magazyn plików, lokalny S3)](6-file-storage-section-done.md)
- [x] [7 — Wielojęzyczność (pl/en, rozszerzalne)](7-i18n-section-done.md)

## Kolejność sekcji w pkt. 3 (od najprostszej do najbardziej złożonej)

1. `authentication` — fundament, wszystko inne wisi na JWT
2. `contact` — najmniejsza domena, dobry poligon pod wzorzec warstw
3. `tools` — prosty CRUD jednej tabeli
4. `aboutme` + `home` — trzeba najpierw rozstrzygnąć duplikat `upload-me`/`information-me`
5. `projects` — największa domena (sub-resource: images, technologies, download)

> Uwaga: mimo numeru **6**, [`file`](6-file-storage-section-done.md) trzeba
> zrobić **przed** 3.3–3.5 — te sekcje potrzebują wspólnego magazynu plików
> zamiast dzisiejszego `open(path, "wb")` rozrzuconego po `routers/`. Zrobione
> — `tools` (3.3) już z niego korzysta.
>
> Podobnie **7** ([wielojęzyczność](7-i18n-section-done.md)) — dotyka już
> zbudowanego `tools` (retrofit: `name`/`information` → `JSONB`
> `{"pl": ..., "en": ...}`) i musi wejść w `aboutme`/`work` (3.4) od razu,
> nie doklejona później. Ustalone: zaczynamy od 7, potem 3.4.

## Referencje

- Wzorzec docelowy: [`docs/ARCHITEKTURA.md`](ARCHITEKTURA.md)
- Stan wyjściowy (do skasowania po migracji): `JWT/`, `routers/`, `DataBase/`
