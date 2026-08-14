from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.cv.response import (
    CurriculumVitaeFileResponse,
    CurriculumVitaeResponse,
    _to_cv_file_response,
    _to_cv_response,
)
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
    """CV to singleton (docs/3.4 pkt. 4.4), jak AboutMe — bez id parametru.

    Zwraca metadane (`file_id`/`url` nullable) — używane przez `handler_upload_cv`
    do sprawdzenia obecnego stanu przed podmianą pliku. Do pobrania samego pliku
    (`GET /api/v1/cv`) służy [[one_cv_file_psql]].
    """
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


def one_cv_file_psql(
    db_session: Session | None = None,
) -> tuple[CurriculumVitaeFileResponse | None, ApiErrorData | None, bool]:
    """Dane pliku aktualnego CV do pobrania (`GET /api/v1/cv` zwraca `FileResponse`).

    Brak CV singletona albo brak przypiętego pliku to tu 404 (`NotFound`) —
    inaczej niż w [[one_cv_psql]], gdzie brak pliku to poprawna wartość `null`.
    """
    try:
        with managed_session(db_session) as (db, _):
            cv = db.execute(select(CurriculumVitae)).scalar_one_or_none()
            if cv is None:
                return (
                    None,
                    ApiErrorData(
                        message="CV not seeded",
                        type_module="one_cv_file_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            file = _load_cv_file(db, cv)
            if file is None:
                return (
                    None,
                    ApiErrorData(
                        message="CV file not set",
                        type_module="one_cv_file_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            return _to_cv_file_response(file), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="one_cv_file_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
