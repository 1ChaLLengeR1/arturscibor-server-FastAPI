"""Wspólna mapa `ApiErrorData.key_type_error` -> HTTP status code.

Endpointy mapują błąd zwrócony przez handler na kod HTTP przez
`STATUS_BY_KEY.get(error.key_type_error, 400)` — klucz nieobecny tutaj
oznacza domyślne 400. Trzymane w jednym miejscu, żeby nie powielać tego
samego słownika (`_STATUS_BY_KEY`) w każdym pliku pod `api/endpoints/`.
"""

STATUS_BY_KEY: dict[str, int] = {
    "NotFound": 404,
    "CvFileMissingOnDisk": 404,
    "AlreadyAttached": 409,
}
