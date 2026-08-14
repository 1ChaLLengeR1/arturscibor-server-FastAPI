from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from config.settings import settings
from core.repository.psql.cv.one import one_cv_file_psql


@dataclass
class CurriculumVitaeFile:
    path: Path
    filename: str
    media_type: str | None


def handler_get_cv(
    db_session: Session | None = None,
) -> tuple[CurriculumVitaeFile | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = one_cv_file_psql(db_session=db_session)
        if not ok:
            return None, err, False

        path = settings.static_root / result.directory / result.name
        if not path.is_file():
            return (
                None,
                ApiErrorData(
                    message="CV file is missing on disk",
                    type_module="handler_get_cv",
                    type_error="missing_on_disk",
                    key_type_error="MissingOnDisk",
                ),
                False,
            )

        return CurriculumVitaeFile(path=path, filename=result.original_name, media_type=result.mime_type), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_get_cv", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
