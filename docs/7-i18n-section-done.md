# 7 — Wielojęzyczność (`pl`/`en`, rozszerzalne)

> Plan, nie implementacja. Cross-cutting — dotyka już zbudowanego `tools`
> (retrofit) i jeszcze niezbudowanego `aboutme`/`work`
> ([`docs/3.4-aboutme-home-section-done.md`](3.4-aboutme-home-section-done.md), do
> wbudowania od razu, nie doklejane później). Ustalone z Arturem: wszystko
> naraz, zaczynając od retrofitu `tools`.
>
> **Wzorzec: JSONB per kolumna, nie osobna tabela tłumaczeń.** Pierwsza
> wersja tego dokumentu proponowała tabelę `tool_translations` (wzorem
> Strapi/WPML) — po analizie kosztu retrofitu `tools` i skali tego
> projektu (jeden admin, garść rekordów) JSONB wygrywa: retrofit to jeden
> `ALTER COLUMN`, nie nowa tabela + backfill + JOIN-y w każdym query.

## 1. Cel

Portfolio ma być dwujęzyczne (`pl` domyślnie, `en`) z możliwością dodania
kolejnych języków bez migracji schematu DB.

## 2. Wzorzec: JSONB `{"pl": "...", "en": "..."}` na tłumaczalnej kolumnie

Każde tłumaczalne pole (`Tools.name`, `Tools.information`,
`AboutMe.job_title`, `AboutMe.body_markdown`, `WorkItem.title`,
`WorkItem.location`, `WorkItem.body_markdown`) zmienia typ z `String` na
`JSONB` (`sqlalchemy.dialects.postgresql.JSONB` — projekt jest Postgres-only,
jak już `ARRAY(String)` przy `WorkItem.skills` w `docs/3.4`), przechowujący
słownik `{język: tekst}`.

```python
from sqlalchemy.dialects.postgresql import JSONB

class Tools(Base):
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[dict[str, str]] = mapped_column(JSONB)               # {"pl": "Python", "en": "Python"}
    information: Mapped[dict[str, str] | None] = mapped_column(JSONB)  # {"pl": "...", "en": "..."}
    progress: Mapped[int | None] = mapped_column(Integer)
    numeric: Mapped[int | None] = mapped_column(Integer)
    link: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

Zero nowych tabel, zero JOIN-ów, zero `tool_translations`/
`about_me_translations`/`work_item_translations` z poprzedniej wersji
tego planu.

**Duże markdown — bez problemu.** JSONB w Postgresie jest TOAST-owany
(kompresowany, poza główną stroną tabeli) automatycznie powyżej ~2KB,
limit realny ~1GB na wartość. Kilka-kilkanaście KB markdowna (`body_markdown`
w `AboutMe`/`WorkItem`) to dla Postgresa nic. Jedyny efekt uboczny: czytasz
cały słownik języków na raz nawet gdy potrzebujesz jednego — przy tej
skali treści nieistotne (kilka KB narzutu, nie setki).

## 3. Walidacja na wejściu — Pydantic, nie FK

Skoro JSONB nie ma FK do `languages.code`, walidacja kluczy przechodzi na
warstwę API — **ustalone: `pl` i `en` zawsze wymagane, dodatkowe klucze
(przyszłe języki) opcjonalne i przechodzą bez zmiany kodu**, przez sam
mechanizm `BaseModel`, bez pisania osobnego `@model_validator`:

```python
from pydantic import BaseModel, ConfigDict


class MultiLangText(BaseModel):
    model_config = ConfigDict(extra="allow")
    __pydantic_extra__: dict[str, str]  # dodatkowe języki poza pl/en — Pydantic 2.6+

    pl: str
    en: str
```

`pl`/`en` jako zwykłe wymagane pola — sam `BaseModel` odrzuci payload bez
któregoś z nich (422, bez dodatkowego kodu). `extra="allow"` +
`__pydantic_extra__: dict[str, str]` — dowolny kolejny klucz (`"de"`,
`"fr"`) jest **przyjmowany i typowany jako `str` automatycznie**, bez
dopisywania pola do modelu. Dla pól opcjonalnych całościowo
(`Tools.information`, `AboutMe.body_markdown`) — `MultiLangText | None`.

**Dodanie trzeciego języka później = zero zmian w kodzie.** JSONB w DB był
bezschematowy od początku; teraz i warstwa walidacji jest — nowy język to
czysto operacyjna sprawa (zacząć wysyłać `"de"` w payloadach przez
istniejący `PUT`, `?lang=de` w query params zadziała od razu przez
fallback z pkt. 4), nie zmiana kodu backendu.

## 4. Fallback — `dict.get()`, nie JOIN

```python
requested = tool.name.get(lang) or tool.name.get(DEFAULT_LANGUAGE_CODE)
```

Bez dodatkowego zapytania — dane już są w pamięci po zwykłym
`SELECT * FROM tools`. `pl` wymagane przez `MultiLangText` (pkt. 3) —
fallback zawsze coś znajdzie, nie ma scenariusza "obu języków brak".

## 5. Bez tabeli `Language` — nic by jej nie czytało

Pierwsza i druga wersja tego planu trzymały `Language` jako tabelę
referencyjną "na wszelki wypadek". Po JSONB przestała mieć jakikolwiek
realny sens:

- **Żadne FK jej nie potrzebuje** — żadna tabela treści nie ma kolumny
  `language_code` (tłumaczenia siedzą w JSONB, nie w osobnych wierszach).
- **`?lang=` nie wymaga walidacji przez DB** — `dict.get(lang)` na
  nieznanym/błędnym kluczu zwraca `None`, co i tak spada do fallbacku na
  `pl` (pkt. 4). Zły język nie wywala niczego — dokładnie ten sam efekt,
  jakby był zwalidowany.
- **Lista znanych języków już żyje w `MultiLangText`** (`pl`, `en`
  wymagane), a kolejne języki przechodzą dynamicznie przez
  `extra="allow"` bez potrzeby wcześniejszej rejestracji gdziekolwiek.

Tabela nie miałaby ani jednego realnego czytelnika w systemie — usunięta
z planu. `DEFAULT_LANGUAGE_CODE = "pl"` zostaje jako zwykła stała w
Pythonie, obok `MultiLangText`:

```python
# api/schemas/common/multi_lang.py
DEFAULT_LANGUAGE_CODE = "pl"


class MultiLangText(BaseModel):
    model_config = ConfigDict(extra="allow")
    __pydantic_extra__: dict[str, str]

    pl: str
    en: str
```

## 6. Retrofit `tools` (już zbudowane)

### Migracja — jeden `ALTER COLUMN` na pole, bez nowej tabeli

```sql
ALTER TABLE tools ALTER COLUMN name TYPE JSONB
  USING jsonb_build_object('pl', name);

ALTER TABLE tools ALTER COLUMN information TYPE JSONB
  USING CASE WHEN information IS NOT NULL
             THEN jsonb_build_object('pl', information)
             ELSE NULL END;
```

Istniejące dane migrują się w locie jako polska wersja (jedyny język, jaki
dotąd istniał) — nic nie ginie, bez osobnego kroku backfill do innej
tabeli.

### Warstwy — co się zmienia

- `core/repository/psql/tools/response.py` — `_to_tool_response` dostaje
  `lang: str` (domyślnie `DEFAULT_LANGUAGE_CODE`), `ToolResponse.name`/
  `information` to wynik fallbacku z pkt. 4, nie surowy JSONB (API nigdy
  nie zwraca całego słownika języków w publicznym `GET` — tylko rozwiązaną
  wartość dla żądanego/domyślnego języka).
- `create_tool_psql` — `name`/`information` przyjmują `MultiLangText`
  (albo już zwalidowany `dict`) zamiast gołego `str` — zapis to jeden
  `INSERT`, bez dodatkowej tabeli.
- `update_tool_psql` — **update jednego języka naraz** (ustalone
  wcześniej, zostaje) realizowany przez `jsonb_set`, nie read-modify-write
  całego słownika w Pythonie (unika race condition przy współbieżnej
  edycji dwóch języków, choć przy jednym adminie to czysto teoretyczne):

  ```python
  from sqlalchemy import func as sa_func

  tool.name = sa_func.jsonb_set(Tools.name, [language_code], sa_func.to_jsonb(new_name))
  ```

  (dokładna składnia SQLAlchemy do doprecyzowania przy pisaniu kodu —
  koncepcja: `jsonb_set(kolumna, '{en}', '"nowy tekst"'::jsonb)` po stronie
  SQL, nie pobieranie-modyfikowanie-zapisywanie całego dicta w Pythonie).

### Endpointy — kontrakt

| Endpoint | Zmiana |
|---|---|
| `POST /admin/tools/create` | `name`/`information` jako `MultiLangText` (`{"pl": "...", "en": "..."}`, oba wymagane od razu) zamiast `str` |
| `PUT /admin/tools/{tool_id}/update` | `+ language_code` (default `pl`) — który język edytujemy tym wywołaniem; `progress`/`numeric`/`link` bez zmian (nietłumaczalne, edytowane niezależnie od języka) |
| `GET /tools/collection` | `+ ?lang=` (default `pl`), zwraca rozwiązane `name`/`information` dla tego języka (z fallbackiem), nie surowy JSONB |

Brak osobnych endpointów `.../translations/{language_code}` z poprzedniej
wersji planu — edycja języka to teraz parametr istniejącego `update`, nie
osobny sub-resource (bo nie ma osobnej tabeli, którą trzeba by adresować
osobno).

**Ochrona `pl`** — inaczej niż poprzednio (tam: nie da się skasować
wiersza `pl` w tabeli tłumaczeń) — teraz to naturalna konsekwencja
`MultiLangText.pl: str` (pole wymagane): nie da się wysłać payloadu bez
`pl`, więc nie da się go "skasować" przez API. Nic dodatkowego do
pilnowania w handlerze.

### Testy

Pakiet testów `tools` (`docs/3.3-tools-section-done.md`) wymaga
przepisania w miejscach, gdzie `name`/`information` są `str` — teraz
`MultiLangText`/`dict`. Mniejszy zakres zmian niż przy wzorcu z tabelą
tłumaczeń (nie trzeba testować JOIN-ów/fallbacku między tabelami, tylko
`dict.get()` + `jsonb_set`).

## 7. `aboutme` / `work` — wbudowane od razu

Aktualizacja modeli z `docs/3.4-aboutme-home-section-done.md` pkt. 4 — pola
oznaczone tam jako tłumaczalne dostają typ `MultiLangText`/`JSONB`
zamiast osobnej tabeli:

```python
class AboutMe(Base):
    __tablename__ = "about_me"
    id: ...
    name: Mapped[str | None] = mapped_column(String)              # NIE tłumaczalne
    job_title: Mapped[dict[str, str] | None] = mapped_column(JSONB)   # {"pl": "...", "en": "..."}
    body_markdown: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    created_at, updated_at


class WorkItem(Base):
    __tablename__ = "work_items"
    id, work_id, employment_type, date_from, date_to, skills  # bez zmian, NIE tłumaczalne
    title: Mapped[dict[str, str]] = mapped_column(JSONB)
    location: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    body_markdown: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    created_at, updated_at
```

Żadnych `AboutMeTranslation`/`WorkItemTranslation` z poprzedniej wersji —
te tabele znikają z planu całkowicie. `Work` (firma, `company_name`)
i `employment_type`/`skills`/daty w `WorkItem` — bez zmian, nietłumaczalne,
jak ustalone wcześniej.

Seed `about_me` — z powrotem **jeden** wiersz (nie dwa jak w poprzedniej
wersji z osobną tabelą tłumaczeń) — `job_title`/`body_markdown` od razu z
kluczem `"pl"` wypełnionym, `"en"` pustym/`None` do uzupełnienia.

## 8. Kolejność implementacji

1. [x] `api/schemas/common/multi_lang.py` — `DEFAULT_LANGUAGE_CODE` +
   `MultiLangText` (Pydantic) razem w jednym pliku. Wstępnie
   `DEFAULT_LANGUAGE_CODE` wydzielony do `core/common/language.py` (obawa
   o warstwy: core importujące z `api/schemas/`), ale to już istniejący,
   zaakceptowany wzorzec w tym repo — `core/repository`/`core/handler`
   swobodnie importują `api.response.ApiErrorData` wszędzie — więc
   scalone z powrotem w jeden plik na prośbę Artura.
2. [x] Retrofit `tools`: migracja `ALTER COLUMN ... TYPE JSONB`
   (`alembic/versions/d356a8a518d6_tools_i18n_jsonb.py`) + repository/
   handler/schematy/endpointy (fallback w `_resolve_lang_text`, update
   jednego języka przez read-modify-write w Pythonie — patrz pkt. 9.2)
3. [x] Testy `tools` — przepisane pod schemat JSONB, plus dedykowane testy
   `pl:{}, en:{}` (raw dict, fallback, update per-język, walidacja
   brakującego/dodatkowego języka)
4. [x] `aboutme` — zbudowane od razu z `JSONB` na `job_title`/`body_markdown`
5. [x] `work` — zbudowane od razu z `JSONB` na `title`/`location`/`body_markdown`
6. [x] `cv` — bez zmian, `CurriculumVitae` nie ma tłumaczalnych pól

## 9. Otwarte pytania (drobne, nie blokują startu)

1. `GET .../collection?lang=en` bez fallbacku wykrytego przez front — czy
   response ma zwracać `resolved_language` (żeby front wiedział, że
   dostał `pl` mimo żądania `en`)? Rekomendacja: tak, przydatne pod
   komunikat "tłumaczenie niedostępne" w UI. **Nadal otwarte.**
2. `jsonb_set` po stronie SQL vs. Python — zaimplementowane jako
   read-modify-write w Pythonie (`{**tool.name, language_code: name}`,
   flush przez SQLAlchemy), nie `jsonb_set` po stronie SQL — prościej,
   czysto teoretyczny race condition przy jednym adminie (patrz pkt. 6 w
   sekcji retrofit). Można podnieść do `jsonb_set` później bez zmiany
   kontraktu API, jeśli kiedyś będzie to potrzebne.

## 10. Status

Gotowe: `tools` (retrofit JSONB + testy), `aboutme` i `work` (zbudowane
od razu z `JSONB` na tłumaczalnych polach, zgodnie z tym planem, bez
oddzielnego retrofitu), `cv` (bez tłumaczalnych pól — nie dotyczy).
Cała sekcja 3 (`tools`/`aboutme`/`work`/`cv`) korzysta teraz z jednego,
spójnego wzorca i18n.
