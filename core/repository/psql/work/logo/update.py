from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.one import _load_work_items, _load_work_logo
from core.repository.psql.work.response import WorkResponse, _to_work_response
from database.psql.database import managed_session
from database.psql.models.work import Work


def set_work_logo_psql(
    work_id: str, file_id: str | None, db_session: Session | None = None
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    """Ustawia (`file_id`) albo czyści (`None`) logo — wzorzec B z docs/3.4 pkt. 3,
    jedna funkcja obsługuje i podmianę, i usunięcie."""
    try:
        with managed_session(db_session) as (db, _):
            work = db.execute(select(Work).where(Work.id == work_id)).scalar_one_or_none()
            if work is None:
                return (
                    None,
                    ApiErrorData(
                        message="Work not found",
                        type_module="set_work_logo_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            work.logo_file_id = file_id
            db.flush()
            db.refresh(work)
            items = _load_work_items(db, work_id)
            logo_file = _load_work_logo(db, work)
            return _to_work_response(work, items, logo_file, lang=DEFAULT_LANGUAGE_CODE), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="set_work_logo_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
