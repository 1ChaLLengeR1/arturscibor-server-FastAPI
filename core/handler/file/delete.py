from sqlalchemy.orm import Session

from api.response import ApiErrorData
from config.settings import settings
from core.repository.psql.file.delete import delete_file_by_id_psql
from core.repository.psql.file.response import DeleteFileResponse


def handler_delete_file(
    file_id: str, db_session: Session | None = None
) -> tuple[DeleteFileResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = delete_file_by_id_psql(file_id=file_id, db_session=db_session)
        if not ok:
            return None, err, False

        file_path = settings.static_root / result.directory / result.name
        try:
            file_path.unlink()
        except FileNotFoundError:
            pass
        except OSError as disk_err:
            if db_session is not None:
                db_session.rollback()
            return (
                None,
                ApiErrorData(
                    message=str(disk_err),
                    type_module="handler_delete_file",
                    type_error="disk_error",
                    key_type_error="DiskError",
                ),
                False,
            )

        return result, None, True

    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_delete_file",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
