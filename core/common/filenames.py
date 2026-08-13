"""Sanityzacja nazwy pliku przychodzącej od klienta (`original_name`).

`original_name` ląduje w trzech miejscach naraz: w ścieżce zapisu na dysku
(`static/files/<directory>/<uuid>_<name>`), w kolumnie `files.name`
(`String(255)`) i w publicznym URL-u. Bez czyszczenia:

  * separator ścieżki robi z nazwy podkatalog — `a/b.png` → zapis do
    `static/files/projects/<uuid>_a/b.png`, którego katalog nie istnieje →
    FileNotFoundError zamiast czytelnego 400,
  * nazwa > 255 znaków wywala INSERT (DataError → 500),
  * spacje/znaki spoza ASCII trafiają do URL-a bez enkodowania.

Prefiks UUID nadawany w handler_init_file sprawia, że `..` samo w sobie nie
wyprowadza poza katalog (pierwszy segment `<uuid>_..` nigdy nie istnieje),
ale nie opieramy na tym bezpieczeństwa — nazwa jest czyszczona jawnie.
"""

import re
from pathlib import PurePosixPath, PureWindowsPath

# Whitelist zamiast blacklisty — wszystko poza [A-Za-z0-9._-] staje się '_'.
_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_REPEATED_SEPARATORS = re.compile(r"([._-])\1+")

_MAX_STEM_LENGTH = 80
_FALLBACK_STEM = "file"


def sanitize_filename(original_name: str, max_stem_length: int = _MAX_STEM_LENGTH) -> str:
    """Zwraca bezpieczną nazwę pliku: bez katalogów, tylko [A-Za-z0-9._-], skróconą.

    Rozszerzenie jest zachowane i zlowercase'owane — walidacja ALLOWED_EXTENSIONS
    powinna działać na wyniku tej funkcji, nie na surowym wejściu.
    """
    # Odcinamy katalogi w obu konwencjach: klient może przysłać "C:\\fotki\\a.png".
    basename = PureWindowsPath(PurePosixPath(original_name).name).name

    stem, dot, suffix = basename.rpartition(".")
    if not dot:
        stem, suffix = basename, ""

    stem = _UNSAFE_CHARS.sub("_", stem)
    stem = _REPEATED_SEPARATORS.sub(r"\1", stem).strip("._-")
    if not stem:
        stem = _FALLBACK_STEM
    stem = stem[:max_stem_length]

    suffix = _UNSAFE_CHARS.sub("_", suffix).lower()

    return f"{stem}.{suffix}" if suffix else stem
