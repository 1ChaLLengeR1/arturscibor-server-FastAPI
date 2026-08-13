from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.response import FileResponse
from core.service.file.upload import upload_file_service


def handler_upload_file(
    file_id: str,
    body: bytes,
    content_type: str,
    db_session: Session | None = None,
) -> tuple[FileResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = upload_file_service(
            file_id=file_id,
            body=body,
            content_type=content_type,
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
                type_module="handler_upload_file",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
