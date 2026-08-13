from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.response import DeleteFileResponse
from database.psql.database import managed_session
from database.psql.models.file import File


def delete_file_by_id_psql(
    file_id: str, db_session: Session | None = None
) -> tuple[DeleteFileResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            file = db.execute(select(File).where(File.id == file_id)).scalar_one_or_none()
            if file is None:
                return (
                    None,
                    ApiErrorData(
                        message="File not found",
                        type_module="delete_file_by_id_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            directory = file.directory
            name = file.name

            db.delete(file)
            db.flush()

            return DeleteFileResponse(deleted=True, id=file_id, directory=directory, name=name), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="delete_file_by_id_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
