from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.response import WorkResponse, _to_work_response
from database.psql.database import managed_session
from database.psql.models.work import Work


def create_work_psql(
    company_name: str, numeric: int | None, db_session: Session | None = None
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            work = Work(company_name=company_name, numeric=numeric)
            db.add(work)
            db.flush()
            db.refresh(work)
            return _to_work_response(work, [], None, lang=DEFAULT_LANGUAGE_CODE), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="create_work_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
