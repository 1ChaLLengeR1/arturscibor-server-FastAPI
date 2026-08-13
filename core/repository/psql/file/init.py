from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.response import FileResponse, _to_file_response
from database.psql.database import managed_session
from database.psql.models.file import File, FileStatus, FileType


def init_file_psql(
    original_name: str,
    name: str,
    size: int,
    directory: str,
    file_type: FileType,
    mime_type: str | None = None,
    db_session: Session | None = None,
) -> tuple[FileResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            new_file = File(
                original_name=original_name,
                name=name,
                size=size,
                directory=directory,
                file_type=file_type,
                mime_type=mime_type,
                status=FileStatus.PENDING,
            )
            db.add(new_file)
            db.flush()
            db.refresh(new_file)
            return _to_file_response(new_file), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="init_file_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
