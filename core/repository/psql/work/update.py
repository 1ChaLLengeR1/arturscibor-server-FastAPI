from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.one import _load_work_items, _load_work_logo
from core.repository.psql.work.response import WorkResponse, _to_work_response
from database.psql.database import managed_session
from database.psql.models.work import Work

_UNSET = object()


def update_work_psql(
    work_id: str,
    company_name: str | None = _UNSET,
    numeric: int | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            work = db.execute(select(Work).where(Work.id == work_id)).scalar_one_or_none()
            if work is None:
                return (
                    None,
                    ApiErrorData(
                        message="Work not found",
                        type_module="update_work_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            if company_name is not _UNSET:
                if not company_name:
                    return (
                        None,
                        ApiErrorData(
                            message="company_name cannot be empty",
                            type_module="update_work_psql",
                            type_error="invalid_value",
                            key_type_error="InvalidValue",
                        ),
                        False,
                    )
                work.company_name = company_name
            if numeric is not _UNSET:
                work.numeric = numeric

            db.flush()
            db.refresh(work)
            items = _load_work_items(db, work_id)
            logo_file = _load_work_logo(db, work)
            return _to_work_response(work, items, logo_file, lang=DEFAULT_LANGUAGE_CODE), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="update_work_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
