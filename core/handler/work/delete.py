from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.work.delete import delete_work_psql
from core.repository.psql.work.one import one_work_by_id_psql


def handler_delete_work(work_id: str, db_session: Session | None = None) -> tuple[None, ApiErrorData | None, bool]:
    """Kasuje firmę + logo (jeśli jest) + wszystkie stanowiska (cascade DB) —
    docs/3.4 pkt. 5. Logo kasowane przez file domain PRZED usunięciem firmy,
    jak podpięte zdjęcia w tools."""
    try:
        work, err, ok = one_work_by_id_psql(work_id, db_session=db_session)
        if not ok:
            return None, err, False

        if work.logo_file_id is not None:
            _, err, ok = handler_delete_file(work.logo_file_id, db_session=db_session)
            if not ok:
                return None, err, False

        _, err, ok = delete_work_psql(work_id, db_session=db_session)
        if not ok:
            return None, err, False

        return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_delete_work", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
