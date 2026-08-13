from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.work.response import WorkResponse
from core.repository.psql.work.update import _UNSET, update_work_psql


def handler_update_work(
    work_id: str,
    company_name: str | None = _UNSET,
    numeric: int | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = update_work_psql(
            work_id, company_name=company_name, numeric=numeric, db_session=db_session
        )
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_update_work", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
