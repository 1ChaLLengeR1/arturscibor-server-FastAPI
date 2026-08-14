from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.work import WorkItem


def delete_work_item_psql(
    work_id: str, item_id: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            item = db.execute(
                select(WorkItem).where(WorkItem.id == item_id, WorkItem.work_id == work_id)
            ).scalar_one_or_none()
            if item is None:
                return (
                    None,
                    ApiErrorData(
                        message="Work item not found",
                        type_module="delete_work_item_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            db.delete(item)
            db.flush()
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="delete_work_item_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
