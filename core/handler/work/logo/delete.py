from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.work.logo.update import set_work_logo_psql
from core.repository.psql.work.one import one_work_by_id_psql
from core.repository.psql.work.response import WorkResponse


def handler_delete_work_logo(
    work_id: str, db_session: Session | None = None
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    try:
        work, err, ok = one_work_by_id_psql(work_id, db_session=db_session)
        if not ok:
            return None, err, False

        if work.logo_file_id is None:
            return (
                None,
                ApiErrorData(
                    message="Work has no logo to remove",
                    type_module="handler_delete_work_logo",
                    type_error="not_found",
                    key_type_error="NotFound",
                ),
                False,
            )

        _, err, ok = handler_delete_file(work.logo_file_id, db_session=db_session)
        if not ok:
            return None, err, False

        return set_work_logo_psql(work_id, None, db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_delete_work_logo",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
