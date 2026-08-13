from sqlalchemy.orm import Session

from api.response import ApiErrorData
from config.settings import settings
from core.repository.psql.file.one import one_file_by_id_psql
from core.repository.psql.file.response import FileResponse
from core.repository.psql.file.update import update_file_by_id_psql
from database.psql.models.file import FileStatus


def handler_confirm_file(
    file_id: str, db_session: Session | None = None
) -> tuple[FileResponse | None, ApiErrorData | None, bool]:
    """Potwierdza plik: PENDING/FAILED nie przechodzą, brak bajtów na dysku też nie.

    Bez tej kontroli confirm ustawiałby CONFIRMED bezwarunkowo — rekord, do którego
    upload nigdy nie doszedł (albo doszedł, ale plik zniknął przy redeployu), dostawałby
    status "potwierdzony" z `url` = NULL. Sprawdzamy więc status ORAZ obecność pliku na dysku.
    """
    try:
        file_data, err, ok = one_file_by_id_psql(file_id=file_id, db_session=db_session)
        if not ok:
            return None, err, False

        # Idempotencja: ponowny confirm (retry frontu) nie jest błędem.
        if file_data.status == FileStatus.CONFIRMED.value:
            return file_data, None, True

        if file_data.status != FileStatus.COMPLETED.value:
            return (
                None,
                ApiErrorData(
                    message=(
                        f"File cannot be confirmed from status '{file_data.status}' "
                        f"(expected '{FileStatus.COMPLETED.value}')"
                    ),
                    type_module="handler_confirm_file",
                    type_error="invalid_status",
                    key_type_error="InvalidStatus",
                ),
                False,
            )

        dest_path = settings.static_root / file_data.directory / file_data.name
        if not dest_path.is_file():
            return (
                None,
                ApiErrorData(
                    message="File is marked as completed but is missing on disk",
                    type_module="handler_confirm_file",
                    type_error="missing_on_disk",
                    key_type_error="MissingOnDisk",
                ),
                False,
            )

        result, err, ok = update_file_by_id_psql(file_id=file_id, status=FileStatus.CONFIRMED, db_session=db_session)
        if not ok:
            return None, err, False

        return result, None, True

    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_confirm_file",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
