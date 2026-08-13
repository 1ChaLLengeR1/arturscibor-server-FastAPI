from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.cv.one import one_cv_psql
from core.repository.psql.cv.response import CurriculumVitaeResponse
from core.repository.psql.cv.update import set_cv_file_psql
from core.repository.psql.file.one import one_file_by_id_psql
from database.psql.models.file import FileStatus, FileType


def handler_upload_cv(
    file_id: str, db_session: Session | None = None
) -> tuple[CurriculumVitaeResponse | None, ApiErrorData | None, bool]:
    """Podmiana CV (wzorzec B, docs/3.4 pkt. 3): stary plik kasowany, jeśli był,
    dopiero potem podpinany nowy."""
    try:
        cv, err, ok = one_cv_psql(db_session=db_session)
        if not ok:
            return None, err, False

        file, err, ok = one_file_by_id_psql(file_id, db_session=db_session)
        if not ok:
            return None, err, False

        if file.file_type != FileType.DOCUMENT.value:
            return (
                None,
                ApiErrorData(
                    message=f"CV must be a document (current file_type: {file.file_type})",
                    type_module="handler_upload_cv",
                    type_error="invalid_file_type",
                    key_type_error="InvalidFileType",
                ),
                False,
            )

        if file.status != FileStatus.CONFIRMED.value:
            return (
                None,
                ApiErrorData(
                    message=f"File must be confirmed before it can be attached (current: {file.status})",
                    type_module="handler_upload_cv",
                    type_error="invalid_status",
                    key_type_error="InvalidStatus",
                ),
                False,
            )

        if cv.file_id is not None:
            _, err, ok = handler_delete_file(cv.file_id, db_session=db_session)
            if not ok:
                return None, err, False

        return set_cv_file_psql(file_id, db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_upload_cv", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
