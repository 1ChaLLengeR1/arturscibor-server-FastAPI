from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.cv.response import CurriculumVitaeResponse, _to_cv_response
from database.psql.database import managed_session
from database.psql.models.cv import CurriculumVitae
from database.psql.models.file import File


def _load_cv_file(db: Session, cv: CurriculumVitae) -> File | None:
    if cv.file_id is None:
        return None
    return db.execute(select(File).where(File.id == cv.file_id)).scalar_one_or_none()


def one_cv_psql(
    db_session: Session | None = None,
) -> tuple[CurriculumVitaeResponse | None, ApiErrorData | None, bool]:
    """CV to singleton (docs/3.4 pkt. 4.4), jak AboutMe — bez id parametru."""
    try:
        with managed_session(db_session) as (db, _):
            cv = db.execute(select(CurriculumVitae)).scalar_one_or_none()
            if cv is None:
                return (
                    None,
                    ApiErrorData(
                        message="CV not seeded",
                        type_module="one_cv_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            file = _load_cv_file(db, cv)
            return _to_cv_response(cv, file), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="one_cv_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
