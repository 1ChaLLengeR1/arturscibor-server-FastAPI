from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.collection import collection_work_psql
from core.repository.psql.work.response import WorkResponse


def handler_collection_work(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[list[WorkResponse] | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = collection_work_psql(lang=lang, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_collection_work",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
