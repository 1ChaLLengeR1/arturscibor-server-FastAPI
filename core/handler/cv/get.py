from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.cv.one import one_cv_psql
from core.repository.psql.cv.response import CurriculumVitaeResponse


def handler_get_cv(
    db_session: Session | None = None,
) -> tuple[CurriculumVitaeResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = one_cv_psql(db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_get_cv", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
