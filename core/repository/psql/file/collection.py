from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.response import FileCollectionResponse, _to_file_response
from database.psql.database import managed_session
from database.psql.models.file import File, FileStatus, FileType

DEFAULT_LIMIT = 32


def collection_files_psql(
    *,
    directory: str | None = None,
    file_type: FileType | None = None,
    status: FileStatus | None = None,
    original_name: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    db_session: Session | None = None,
) -> tuple[FileCollectionResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            query = select(File)

            if directory is not None:
                query = query.where(File.directory == directory)
            if file_type is not None:
                query = query.where(File.file_type == file_type)
            if status is not None:
                query = query.where(File.status == status)
            if original_name is not None:
                query = query.where(File.original_name.ilike(f"%{original_name}%"))

            total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

            query = query.order_by(File.created_at.desc()).limit(limit).offset(offset)
            files = db.execute(query).scalars().all()

            return (
                FileCollectionResponse(items=[_to_file_response(file) for file in files], total=total),
                None,
                True,
            )
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="collection_files_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
