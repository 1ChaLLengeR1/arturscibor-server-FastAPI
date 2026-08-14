from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.work.create import create_work_psql
from core.repository.psql.work.response import WorkResponse


def handler_create_work(
    company_name: str, numeric: int | None, db_session: Session | None = None
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = create_work_psql(company_name, numeric, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_create_work", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
