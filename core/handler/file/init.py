import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.common.filenames import sanitize_filename
from core.repository.psql.file.init import init_file_psql
from core.repository.psql.file.response import FileInitResponse
from database.psql.models.file import ALLOWED_DIRECTORIES, ALLOWED_EXTENSIONS, FileType

# Rodzina MIME wymagana dla danego typu pliku. `mime_type` pochodzi od klienta i jest
# potem porównywany z Content-Type uploadu — bez tej kontroli dałoby się zadeklarować
# np. "text/html" dla .png i wymusić taki nagłówek przy zapisie.
_MIME_FAMILY_BY_FILE_TYPE: dict[FileType, str] = {
    FileType.PHOTO: "image/",
    FileType.VIDEO: "video/",
}


def handler_init_file(
    original_name: str,
    size: int,
    directory: str,
    file_type: FileType,
    mime_type: str | None = None,
    db_session: Session | None = None,
) -> tuple[FileInitResponse | None, ApiErrorData | None, bool]:
    try:
        if directory not in ALLOWED_DIRECTORIES:
            return (
                None,
                ApiErrorData(
                    message=f"Directory '{directory}' is not allowed. Allowed: {sorted(ALLOWED_DIRECTORIES)}",
                    type_module="handler_init_file",
                    type_error="invalid_directory",
                    key_type_error="InvalidDirectory",
                ),
                False,
            )

        # Najpierw czyścimy nazwę, potem walidujemy rozszerzenie — inaczej sprawdzalibyśmy
        # co innego, niż faktycznie ląduje na dysku.
        safe_name = sanitize_filename(original_name)

        extension = Path(safe_name).suffix.lower()
        allowed = ALLOWED_EXTENSIONS.get(file_type, set())
        if extension not in allowed:
            return (
                None,
                ApiErrorData(
                    message=(
                        f"Extension '{extension}' is not allowed for file_type "
                        f"'{file_type.value}'. Allowed: {sorted(allowed)}"
                    ),
                    type_module="handler_init_file",
                    type_error="invalid_extension",
                    key_type_error="InvalidExtension",
                ),
                False,
            )

        # Normalizacja MIME (bez parametrów typu "; charset=..."), żeby porównanie
        # z Content-Type na uploadzie nie wywracało się na formatowaniu nagłówka.
        normalized_mime = mime_type.split(";")[0].strip().lower() if mime_type else None
        if normalized_mime:
            expected_family = _MIME_FAMILY_BY_FILE_TYPE[file_type]
            if not normalized_mime.startswith(expected_family):
                return (
                    None,
                    ApiErrorData(
                        message=(
                            f"MIME type '{normalized_mime}' does not match file_type "
                            f"'{file_type.value}' (expected '{expected_family}*')"
                        ),
                        type_module="handler_init_file",
                        type_error="invalid_mime_type",
                        key_type_error="InvalidMimeType",
                    ),
                    False,
                )

        unique_name = f"{uuid.uuid4()}_{safe_name}"

        file_data, err, ok = init_file_psql(
            original_name=original_name,
            name=unique_name,
            size=size,
            directory=directory,
            file_type=file_type,
            mime_type=normalized_mime,
            db_session=db_session,
        )
        if not ok:
            return None, err, False

        upload_url = f"/api/v1/admin/file/{file_data.id}/upload"
        public_url = f"/static/{directory}/{unique_name}"

        return (
            FileInitResponse(file_id=file_data.id, upload_url=upload_url, public_url=public_url),
            None,
            True,
        )

    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_init_file",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
