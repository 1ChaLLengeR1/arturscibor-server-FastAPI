from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.collection import DEFAULT_LIMIT, collection_files_psql
from core.repository.psql.file.response import FileCollectionResponse
from database.psql.models.file import FileStatus, FileType


def handler_collection_files(
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
        result, err, ok = collection_files_psql(
            directory=directory,
            file_type=file_type,
            status=status,
            original_name=original_name,
            limit=limit,
            offset=offset,
            db_session=db_session,
        )
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_collection_files",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
