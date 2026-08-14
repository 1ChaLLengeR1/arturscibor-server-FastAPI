from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.file.one import one_file_by_id_psql
from core.repository.psql.work.logo.update import set_work_logo_psql
from core.repository.psql.work.one import one_work_by_id_psql
from core.repository.psql.work.response import WorkResponse
from database.psql.models.file import FileStatus


def handler_update_work_logo(
    work_id: str, file_id: str, db_session: Session | None = None
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    """Podmiana logo (wzorzec B, docs/3.4 pkt. 3): stare kasowane, jeśli było,
    dopiero potem podpinane nowe."""
    try:
        work, err, ok = one_work_by_id_psql(work_id, db_session=db_session)
        if not ok:
            return None, err, False

        file, err, ok = one_file_by_id_psql(file_id, db_session=db_session)
        if not ok:
            return None, err, False

        if file.status != FileStatus.CONFIRMED.value:
            return (
                None,
                ApiErrorData(
                    message=f"File must be confirmed before it can be attached (current: {file.status})",
                    type_module="handler_update_work_logo",
                    type_error="invalid_status",
                    key_type_error="InvalidStatus",
                ),
                False,
            )

        if work.logo_file_id is not None:
            _, err, ok = handler_delete_file(work.logo_file_id, db_session=db_session)
            if not ok:
                return None, err, False

        return set_work_logo_psql(work_id, file_id, db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_update_work_logo",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
