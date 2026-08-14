from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.cv.one import _load_cv_file
from core.repository.psql.cv.response import CurriculumVitaeResponse, _to_cv_response
from database.psql.database import managed_session
from database.psql.models.cv import CurriculumVitae


def set_cv_file_psql(
    file_id: str | None, db_session: Session | None = None
) -> tuple[CurriculumVitaeResponse | None, ApiErrorData | None, bool]:
    """Ustawia (`file_id`) albo czyści (`None`) CV — wzorzec B z docs/3.4 pkt. 3."""
    try:
        with managed_session(db_session) as (db, _):
            cv = db.execute(select(CurriculumVitae)).scalar_one_or_none()
            if cv is None:
                return (
                    None,
                    ApiErrorData(
                        message="CV not seeded",
                        type_module="set_cv_file_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            cv.file_id = file_id
            db.flush()
            db.refresh(cv)
            file = _load_cv_file(db, cv)
            return _to_cv_response(cv, file), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="set_cv_file_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
