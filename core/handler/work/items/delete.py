from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.work.items.delete import delete_work_item_psql


def handler_delete_work_item(
    work_id: str, item_id: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    try:
        result, err, ok = delete_work_item_psql(work_id, item_id, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_delete_work_item",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
