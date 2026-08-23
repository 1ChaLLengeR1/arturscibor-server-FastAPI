from datetime import date

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.response import ProjectResponse
from core.repository.psql.projects.update import _UNSET, update_project_psql
from database.psql.models.projects import ProjectLevel


def handler_update_project(
    project_id: str,
    language_code: str = DEFAULT_LANGUAGE_CODE,
    name: str | None = _UNSET,
    short_description: str | None = _UNSET,
    description: str | None = _UNSET,
    level: ProjectLevel | None = _UNSET,
    technologies: list[str] | None = _UNSET,
    github_url: str | None = _UNSET,
    live_url: str | None = _UNSET,
    completed_at: date | None = _UNSET,
    started_at: date | None = _UNSET,
    is_support: bool | None = _UNSET,
    numeric: int | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = update_project_psql(
            project_id,
            language_code=language_code,
            name=name,
            short_description=short_description,
            description=description,
            level=level,
            technologies=technologies,
            github_url=github_url,
            live_url=live_url,
            completed_at=completed_at,
            started_at=started_at,
            is_support=is_support,
            numeric=numeric,
            db_session=db_session,
        )
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_update_project",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
