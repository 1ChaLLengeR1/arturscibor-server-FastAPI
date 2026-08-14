from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.work import Work


def delete_work_psql(work_id: str, db_session: Session | None = None) -> tuple[None, ApiErrorData | None, bool]:
    """Kasuje wiersz firmy — `work_items` znikają przez `ON DELETE CASCADE`.
    Kasowanie logo (jeśli jest) to zadanie handlera (cross-domain, jak w tools)."""
    try:
        with managed_session(db_session) as (db, _):
            work = db.execute(select(Work).where(Work.id == work_id)).scalar_one_or_none()
            if work is None:
                return (
                    None,
                    ApiErrorData(
                        message="Work not found",
                        type_module="delete_work_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            db.delete(work)
            db.flush()
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="delete_work_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
