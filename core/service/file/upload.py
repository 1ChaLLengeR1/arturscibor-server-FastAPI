from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from config.settings import settings
from core.repository.psql.file.response import FileResponse
from core.repository.psql.file.update import update_file_by_id_psql
from database.psql.database import managed_session
from database.psql.models.file import ALLOWED_DIRECTORIES, MAX_FILE_SIZE_BYTES, File, FileStatus

# Klient wysyłający surowe bajty często nie zna (albo nie ustawia) konkretnego typu —
# endpoint deklaruje application/octet-stream. Traktujemy takie nagłówki jako "brak
# deklaracji" i opieramy się na mime_type ustalonym w /init (tam jest walidowany
# względem file_type i rozszerzenia).
_GENERIC_CONTENT_TYPES = {"", "application/octet-stream", "binary/octet-stream"}


def upload_file_service(
    file_id: str,
    body: bytes,
    content_type: str,
    db_session: Session | None = None,
) -> tuple[FileResponse | None, ApiErrorData | None, bool]:
    try:
        normalized_content_type = content_type.split(";")[0].strip().lower()
        with managed_session(db_session) as (db, _):
            file = db.execute(select(File).where(File.id == file_id)).scalar_one_or_none()

            if not file:
                return (
                    None,
                    ApiErrorData(
                        message="File not found",
                        type_module="upload_file_service",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            if file.status != FileStatus.PENDING:
                return (
                    None,
                    ApiErrorData(
                        message=f"File is not in pending state (current: {file.status.value})",
                        type_module="upload_file_service",
                        type_error="invalid_status",
                        key_type_error="InvalidStatus",
                    ),
                    False,
                )

            if (
                file.mime_type
                and normalized_content_type not in _GENERIC_CONTENT_TYPES
                and normalized_content_type != file.mime_type
            ):
                return (
                    None,
                    ApiErrorData(
                        message=f"Content-Type mismatch: expected {file.mime_type}, got {content_type}",
                        type_module="upload_file_service",
                        type_error="mime_type_mismatch",
                        key_type_error="MimeTypeMismatch",
                    ),
                    False,
                )

            if len(body) > MAX_FILE_SIZE_BYTES:
                return (
                    None,
                    ApiErrorData(
                        message=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB",
                        type_module="upload_file_service",
                        type_error="file_too_large",
                        key_type_error="FileTooLarge",
                    ),
                    False,
                )

            if len(body) != file.size:
                return (
                    None,
                    ApiErrorData(
                        message=f"File size mismatch: expected {file.size} bytes, got {len(body)}",
                        type_module="upload_file_service",
                        type_error="size_mismatch",
                        key_type_error="SizeMismatch",
                    ),
                    False,
                )

            # Twarda kontrola katalogu: `directory` w rekordzie może pochodzić z innego
            # źródła niż handler_init_file, a stąd budujemy ścieżkę zapisu — bez tego
            # dałoby się pisać poza drzewem static/files/.
            if file.directory not in ALLOWED_DIRECTORIES:
                return (
                    None,
                    ApiErrorData(
                        message=f"Directory '{file.directory}' is not allowed. Allowed: {sorted(ALLOWED_DIRECTORIES)}",
                        type_module="upload_file_service",
                        type_error="invalid_directory",
                        key_type_error="InvalidDirectory",
                    ),
                    False,
                )

            dest_dir = settings.static_root / file.directory
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / file.name
            dest_path.write_bytes(body)

            public_url = f"/static/{file.directory}/{file.name}"

        return update_file_by_id_psql(
            file_id=file_id,
            url=public_url,
            status=FileStatus.COMPLETED,
            db_session=db_session,
        )

    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="upload_file_service",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
