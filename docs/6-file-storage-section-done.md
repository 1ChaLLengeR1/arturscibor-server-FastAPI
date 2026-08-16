# 6 — Sekcja: `file` (magazyn plików, lokalny odpowiednik S3)

> Zweryfikowane 1:1 na podstawie realnych plików źródłowych repo
> referencyjnego (`~/Desktop/BackendWhereIsWilly`, WhereIsWheely Backend
> API) — nie domysłów z nazw plików. Przeczytane: `api/endpoints/file/*.py`,
> `core/handler/file/*.py`, `core/service/file/upload.py`,
> `core/repository/psql/file/*.py`, `database/psql/models/file.py`,
> `core/common/filenames.py`, `api/schemas/file/schemas.py`,
> `api/endpoints/urls.py`, `config/settings.py`, `main.py`, testy w
> `tests/core/{common,handler,repository/psql,service}/file/` i
> `tests/api/endpoints/file/`. Poniżej: mechanizm z referencji + konkretne
> adaptacje do tego repo (portfolio jednego admina, nie multi-tenant sklep).

## 1. Cel

Zbudować wspólny, warstwowy mechanizm przechowywania plików na lokalnym
dysku (`static/files/`), używany przez wszystkie domeny, które dziś zapisują
pliki "na piechotę" (`open(path, "wb")` rozrzucone po `routers/Projects`,
`routers/Home`, `routers/Tools`, `routers/AboutMe`). Docelowo `projects`
(3.5), `aboutme`/`home` (3.4) i `tools` (3.3) będą wołać ten mechanizm
zamiast pisać własną logikę zapisu na dysk.

## 2. Flow: init → upload → confirm (+ delete, collection)

Dokładnie jak S3 presigned upload, trzy fazy + status `FAILED` (zdefiniowany,
ale w referencji nigdzie automatycznie nieustawiany — zarezerwowany pod
przyszły cleanup/cron):

1. **`POST /files/init`** (`handler_init_file`) — klient deklaruje
   `original_name`, `size`, `directory`, `file_type`, opcjonalnie
   `mime_type`. Walidacja: `directory ∈ ALLOWED_DIRECTORIES`, sanityzacja
   nazwy (`sanitize_filename`), rozszerzenie ∈ `ALLOWED_EXTENSIONS[file_type]`,
   rodzina MIME zgodna z `file_type`. Generuje `name = f"{uuid4()}_{safe_name}"`,
   tworzy rekord DB status `PENDING` (`init_file_psql`, zero I/O na dysku).
   Zwraca `file_id`, `upload_url`, `public_url`.
2. **`PUT /files/{file_id}/upload`** (`handler_upload_file` →
   `upload_file_service`) — **jedyne miejsce, które dotyka dysku**. Klient
   wysyła surowe bajty (`request.body()`, Content-Type
   `application/octet-stream`). Walidacja: rekord istnieje i ma status
   `PENDING`, Content-Type zgadza się z `mime_type` z init (chyba że
   generyczny `octet-stream`), `len(body) <= MAX_FILE_SIZE_BYTES`,
   `len(body) == f.size` (dokładna zgodność z deklaracją z init — nie tylko
   limit), `directory` ponownie sprawdzony przeciw `ALLOWED_DIRECTORIES`
   (**druga, niezależna kontrola** — bo `directory` rekordu może pochodzić
   z innego źródła niż `init`, np. przyszły `admin/files/create`). Zapis:
   `settings.static_root / directory / name`. Aktualizuje rekord na status
   `COMPLETED` + `url = /static/{directory}/{name}` (`update_file_by_id_psql`).
3. **`PATCH /files/{file_id}/confirm`** (`handler_confirm_file`) —
   potwierdza, że plik jest finalnie przypięty. Idempotentny (ponowny
   confirm na już-`CONFIRMED` zwraca sukces, nie błąd). Odrzuca, jeśli
   status ≠ `COMPLETED`. Dodatkowo **sprawdza realną obecność pliku na
   dysku** przed ustawieniem `CONFIRMED` — zabezpiecza przed rekordem, do
   którego upload nigdy nie doszedł albo plik zniknął przy redeployu.
4. **`DELETE /files/{file_id}/delete`** (`handler_delete_file`) — najpierw
   kasuje rekord DB (`delete_file_by_id_psql`), potem usuwa plik z dysku.
   `FileNotFoundError` ignorowany (rekord bez pliku to nie błąd), inny
   `OSError` → `db_session.rollback()` + błąd (żeby DB i dysk nie rozjechały
   się w connected-ale-nie-flushed stanie).
5. **`GET /files/collection`** (`handler_collection_files` →
   `collection_files_psql`) — listing z filtrami `directory`, `file_type`,
   `status`, `original_name` (ILIKE), `limit`/`offset`, `total` +
   `has_more`.

Pliki ze statusem `CONFIRMED` są serwowane statycznie przez mount
`/static`, bez przechodzenia przez żadną z powyższych warstw.

## 3. Model danych — `database/psql/models/file.py`

Kopia z referencji, z jedną świadomą adaptacją (patrz pkt. 4):

```python
class FileStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFIRMED = "confirmed"

class FileType(str, enum.Enum):
    PHOTO = "photo"
    GIF = "gif"
    VIDEO = "video"
    AUDIO = "audio"

ALLOWED_DIRECTORIES: set[str] = {...}          # pkt. 8 — do potwierdzenia dla tego projektu
ALLOWED_EXTENSIONS: dict[FileType, set[str]] = {
    FileType.PHOTO: {".jpg", ".jpeg", ".png", ".webp"},
    FileType.GIF:   {".gif"},
    FileType.VIDEO: {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"},
    FileType.AUDIO: {".mp3", ".wav", ".aac", ".m4a"},
}
MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB — do potwierdzenia
```

Tabela `files`: `id` (UUID PK), `original_name` (String 255),
`name` (String 255, unique — `{uuid4}_{sanitized}`), `size` (BigInteger),
`mime_type` (nullable), `url` (nullable, ustawiany dopiero po uploadzie),
`directory` (String 64), `file_type` (Enum), `status` (Enum, default
`PENDING`), `created_at`/`updated_at`. Indeksy na `status`, `file_type`,
`directory`.

**Adaptacja vs. referencja:** oryginał ma `user_id: UUID | None` +
relację `categories: list["Category"]` (WhereIsWilly to sklep z wieloma
zwykłymi userami, którzy mogą "posiadać" pliki, plus FK do `Category`).
W tym repo `Users.type` to tylko `guest`/`admin` (`database/psql/models/users.py`)
— nie ma koncepcji zwykłego użytkownika przesyłającego własne pliki, więc
**rekomenduję pominąć `user_id` i relację `categories` całkowicie**. Cała
logika `is_admin`/`is_owner` w repository referencji (widoczna w
`one.py`, `delete.py`, `collection.py`, `upload.py`) odpada — dostęp
kontrolowany wyłącznie na poziomie endpointu przez
`JWTAuthenticationMiddleware(roles=["admin"])`, dokładnie jak już działa
`admin/contact`. To zadanie do potwierdzenia — patrz pkt. 9.1.

## 4. `core/common/filenames.py` — `sanitize_filename` (nowy plik)

Nie istnieje jeszcze w tym repo (`core/common/` ma dziś tylko
`bcrypt_password.py`, `jwt.py`). Kopiować z referencji 1:1 — czysta funkcja,
zero zależności od DB/configu:

- Whitelist zamiast blacklisty: wszystko poza `[A-Za-z0-9._-]` → `_`.
- Ucina segmenty katalogów w obu konwencjach (`PurePosixPath` +
  `PureWindowsPath`) — klient mógłby przysłać `"C:\\fotki\\a.png"` albo
  `"../../a.png"`.
- Rdzeń nazwy maks. 80 znaków, fallback `"file"` gdy nazwa po czyszczeniu
  jest pusta.
- Rozszerzenie zachowane i zlowercase'owane.

Prefiks `uuid4()` nadawany w `handler_init_file` (pkt. 2.1) jest dodatkową
warstwą przeciw path traversal, ale sanityzacja nie polega na tym — nazwa
jest czyszczona jawnie, niezależnie.

## 5. Warstwy i pliki docelowe

| Plik | Rola (z referencji) |
|---|---|
| `database/psql/models/file.py` | `File`, `FileStatus`, `FileType`, `ALLOWED_DIRECTORIES`, `ALLOWED_EXTENSIONS`, `MAX_FILE_SIZE_BYTES` |
| `core/common/filenames.py` | `sanitize_filename` — nowy plik (pkt. 4) |
| `core/repository/psql/file/response.py` | `FileResponse`, `FileCollectionResponse`, `FileInitResponse`, `DeleteFileResponse` (dataclassy) + `_to_file_response` |
| `core/repository/psql/file/init.py` | `init_file_psql` — INSERT, status `PENDING` |
| `core/repository/psql/file/one.py` | `one_file_by_id_psql` — SELECT po id (uproszczone: bez `is_admin`/`is_owner`, patrz pkt. 3) |
| `core/repository/psql/file/update.py` | `update_file_by_id_psql` — patch `url`/`status` |
| `core/repository/psql/file/delete.py` | `delete_file_by_id_psql` — DELETE rekordu, zwraca `directory`+`name` do skasowania z dysku |
| `core/repository/psql/file/collection.py` | `collection_files_psql` — listing z filtrami + `total` |
| `core/service/file/upload.py` | `upload_file_service` — **jedyna warstwa I/O na dysku**: walidacja Content-Type/rozmiar/directory + zapis bajtów + wywołanie `update_file_by_id_psql`. W `service/`, nie `handler/`, bo dotyka zasobu poza DB |
| `core/handler/file/init.py` | `handler_init_file` — walidacja `directory`/rozszerzenia/MIME + `sanitize_filename` + `init_file_psql`, buduje `upload_url`/`public_url` |
| `core/handler/file/upload.py` | `handler_upload_file` — cienki wrapper nad `upload_file_service` |
| `core/handler/file/confirm.py` | `handler_confirm_file` — idempotencja + sprawdzenie pliku na dysku + `update_file_by_id_psql` |
| `core/handler/file/delete.py` | `handler_delete_file` — `delete_file_by_id_psql` + fizyczne usunięcie z dysku (obsługa `FileNotFoundError`/`OSError`) |
| `core/handler/file/collection.py` | `handler_collection_files` — cienki wrapper nad `collection_files_psql` |
| `api/schemas/file/schemas.py` | `FileInitPayload`, `FileInitResponseData`, `FileItemData`, `PaginationData`, `FileCollectionResponseData`, `DeleteFileResponseData` |
| `api/endpoints/file/init.py` | `POST` |
| `api/endpoints/file/upload.py` | `PUT` (raw bytes, `openapi_extra` deklarujące `application/octet-stream`) |
| `api/endpoints/file/confirm.py` | `PATCH` |
| `api/endpoints/file/delete.py` | `DELETE` |
| `api/endpoints/file/collection.py` | `GET` |

Warstwa `core/handler/file/` **istnieje** w referencji (rozstrzyga to
otwarte pytanie z wcześniejszej wersji tego planu, gdy jeszcze zgadywałem
z samych nazw plików) — każdy endpoint woła handler, handler woła
repository (albo `service` w przypadku uploadu), zgodnie z ogólnym wzorcem
3-warstwowym z `docs/ARCHITEKTURA.md` §4.

## 6. Endpointy i URL-e

Z referencji (`api/endpoints/urls.py:142-147`), 1:1:

```
FILES_INIT       = "/api/v1/files/init"                  # POST
FILES_UPLOAD     = "/api/v1/files/{file_id}/upload"       # PUT
FILES_CONFIRM    = "/api/v1/files/{file_id}/confirm"      # PATCH
FILES_COLLECTION = "/api/v1/files/collection"              # GET
FILES_DELETE     = "/api/v1/files/{file_id}/delete"        # DELETE
```

Tag Swagger: `Files`.

**Uwaga o konwencji URL:** ten projekt prefiksuje endpointy admin-only
przez `/admin/` (`ADMIN_CONTACT_*`), referencja tego nie robi (auth i tak
wymuszony przez middleware, nie przez prefiks ścieżki). Rekomendacja:
zachować `FILES_*` bez `/admin/` — user chciał "dokładnie ten sam
mechanizm", a prefiks w URL nic nie zmienia w bezpieczeństwie. Do
potwierdzenia w pkt. 9.5, jeśli wolisz spójność z `ADMIN_CONTACT_*`.

**Auth — adaptacja:** referencja używa `JWTAuthenticationMiddleware()` bez
`roles` (każdy zalogowany user), potem ręcznie sprawdza `is_admin`/
`is_owner` w repository na podstawie `current_user["id"]`/`current_user["role"]`.
W tym repo `JWTAuthenticationMiddleware.__call__` zwraca
`{"id_user": ..., "type": ...}` (inne klucze niż referencja!) i **już
wspiera** `roles=["admin"]` jako parametr konstruktora (patrz
`api/middleware/Authentication.py:18,40`) — dokładnie jak `admin/contact`.
Rekomendacja: `Depends(JWTAuthenticationMiddleware(roles=["admin"]))` na
wszystkich pięciu endpointach, bez przekazywania
`requesting_user_id`/`requesting_user_role` dalej w ogóle — upraszcza
sygnatury wszystkich repository/handler/service funkcji (bez parametrów
ownership, patrz pkt. 3).

## 7. Konfiguracja i `main.py`

`config/settings.py` (ten projekt używa `env_prefix`, nie per-pole
`alias` jak referencja) — dodać:

```python
static_root: Path = BASE_DIR / "static" / "files"
```

`main.py` — dokładnie wzorzec podany w zadaniu (zweryfikowany jako
identyczny z prawdziwym `main.py` referencji):

```python
from database.psql.models.file import ALLOWED_DIRECTORIES
...
_STATIC_ROOT = settings.static_root
_STATIC_ROOT.mkdir(parents=True, exist_ok=True)
for _directory in sorted(ALLOWED_DIRECTORIES):
    (_STATIC_ROOT / _directory).mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_STATIC_ROOT)), name="static")
```

Stary `app.mount("/file", StaticFiles(directory="file"), name="file")` —
do usunięcia (zastąpiony przez `/static`), `file/.gitkeep` do skasowania
razem z nim.

## 8. Rate limiting — brakująca zależność w tym repo

Referencja dekoruje każdy endpoint `@limiter.limit("30/minute")`
(collection: `"60/minute"`) przez `slowapi`, z `config/rate_limit.py` +
`app.state.limiter` + `SlowAPIMiddleware` w `main.py`. **Ten projekt nie ma
`slowapi` w `pyproject.toml` ani `config/rate_limit.py` w ogóle** — żaden
istniejący endpoint (auth, contact) go nie używa.

Dwie opcje:
- (a) **Pominąć rate limiting w tym zadaniu** — dodać jako osobny,
  przekrojowy task infra (dotyczyłby też auth/contact, nie tylko file).
- (b) Dorzucić `slowapi` + `config/rate_limit.py` + wiring w `main.py` jako
  prerequisite tego zadania.

Rekomendacja: (a).

## 9. Otwarte pytania (zredukowane — większość rozstrzygnięta przez odczyt źródeł)

1. **Usunięcie `user_id`/ownership z modelu `File`** (pkt. 3) — potwierdzić,
   że to CMS jednego admina i nie potrzebujemy właścicieli plików.
2. **`ALLOWED_DIRECTORIES`** — propozycja `{"projects", "aboutme", "tools"}`
   (docs/roadmap.md 3.3–3.5). Referencja miała `{"categories", "products",
   "users"}` (specyficzne dla sklepu).
3. **`FileType.DOCUMENT` (PDF)** — referencja nie ma tego typu, ale stary
   kod tego repo (`routers/Home/information_cv.py`, CV; potencjalnie
   `routers/Projects/download_project.py`, plik do pobrania) sugeruje
   potrzebę PDF-ów. Dodać `DOCUMENT = "document"` z `{".pdf"}` do
   `ALLOWED_EXTENSIONS`?
4. **Rate limiting** — pomijamy teraz (rekomendacja, pkt. 8) czy dodajemy
   jako prerequisite?
5. **URL-e** — zachować `FILES_*` bez `/admin/` jak w referencji
   (rekomendacja, pkt. 6), czy przejść na `ADMIN_FILE_*` zgodnie z lokalną
   konwencją nazewnictwa?
6. **`MAX_FILE_SIZE_BYTES`** — zostawić 25 MB jak w referencji, czy niżej
   (portfolio raczej nie potrzebuje ciężkich wideo)?

## 10. Testy — lustrzana struktura z referencji

- `tests/core/common/test_filenames.py`
- `tests/core/repository/psql/file/helper.py` (`create_test_file`) +
  `test_{init_file_psql,one_file_by_id_psql,update_file_by_id_psql,
  delete_file_by_id_psql,collection_files_psql}.py`
- `tests/core/handler/file/test_{confirm_file,delete_file}.py` (referencja
  ma testy handlera tylko dla confirm/delete — warto dołożyć też
  init/upload/collection nawet jeśli oryginał tego nie miał)
- `tests/core/service/file/test_upload_file_service.py` — fixture
  `cleanup_static` czyszcząca `static/files/{directory}/` po każdym teście
  (poza `.gitkeep`), plik testowy binarny w `tests/files_for_tests/`
- `tests/api/endpoints/file/test_api_{init,upload,confirm,delete,
  collection}_file.py` + `helper.py` (`make_client`, wzorem
  `tests/api/endpoints/contact/helper.py`)

## 11. Kolejność prac

- [x] Rozstrzygnąć pkt. 9 (6 pytań) — patrz pkt. 12
- [x] `core/common/filenames.py` (`sanitize_filename`) + test
- [x] `database/psql/models/file.py` + migracja alembic
- [x] `core/repository/psql/file/{response,init,one,update,delete,collection}.py` + testy
- [x] `core/service/file/upload.py` + testy
- [x] `core/handler/file/{init,upload,confirm,delete,collection}.py`
- [x] `api/schemas/file/{response,init,collection,delete}.py`
- [x] `api/endpoints/admin/file/{init,upload,confirm,delete,collection}.py` +
      `api/endpoints/urls.py` + `api/router.py` + testy e2e
- [x] `config/settings.py` (`static_root`) + `main.py` (mount `/static`,
      usunięcie starego `/file` i `file/.gitkeep`)
- [x] `.gitignore` dla zawartości `static/files/**`
- [x] Podłączenie pod 3.3 (`tools`, patrz `docs/3.3-tools-section-done.md`)
      — 3.4/3.5 zostają osobnymi zadaniami

## 12. Status końcowy — decyzje i odchylenia od planu wstępnego

Pytania z pkt. 9/10 (wersji roboczej tego dokumentu) rozstrzygnięte wprost
przez Artura, implementacja odbiega od pierwotnej propozycji "1:1 z
referencją" w kilku miejscach:

- **`FileType`**: tylko `PHOTO`/`VIDEO` — bez `GIF`/`AUDIO`, bez
  `DOCUMENT`(PDF) mimo starego kodu CV. Jeśli PDF-y (CV, download projektu)
  okażą się potrzebne w 3.4/3.5, to osobna decyzja wtedy.
- **`user_id`/ownership — usunięte całkowicie**, nie tylko z modelu `File`
  (jak zakładał plan wstępny), tożsamość admina idzie wyłącznie przez
  `JWTAuthenticationMiddleware(roles=["admin"])` na endpointzie, bez
  przechowywania jej gdziekolwiek.
- **Struktura endpointów**: `api/endpoints/admin/file/` (nie
  `api/endpoints/file/` jak w referencji) — spójnie z lokalną konwencją
  `admin/contact`. URL-e: `ADMIN_FILE_*` pod `/api/v1/admin/file/...`, nie
  `FILES_*` pod `/api/v1/files/...` z referencji.
- **`api/schemas/file/`**: rozbite na `{response,init,collection,delete}.py`
  zamiast jednego `schemas.py` — zgodnie z konwencją "większe domeny
  dostają osobne pliki" (`docs/3.5-projects-section-done.md`).
- **Rate limiting**: pominięty (rekomendacja z pkt. 8), do osobnego brancha.
- **CORS w `main.py`**: przy okazji zaostrzony — skończona lista originów
  (`settings.frontend_url` + localhost dev) i metod/nagłówków zamiast
  `allow_origins=[]` + `allow_methods/headers=["*"]`.
- **Testy**: napisane w całości (repository, service, e2e API), z realnym
  plikiem testowym w `tests/files_for_tests/` — nie odłożone "na koniec",
  bo to była pierwsza migrowana domena z realnym I/O na dysku i chciałem
  mieć pewność co do flow init→upload→confirm zanim `tools` (3.3) zaczęło
  go używać.

Kod zlintowany (`ruff check .` czysty), `main.py` importuje się i
wystawia poprawny zestaw tras, migracja zweryfikowana offline w obie
strony. Odpalenie migracji i testów na żywej bazie — po Twojej stronie.
