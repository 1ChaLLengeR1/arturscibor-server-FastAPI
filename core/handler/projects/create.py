from datetime import date

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.projects.create import create_project_psql
from core.repository.psql.projects.response import ProjectResponse
from database.psql.models.projects import ProjectLevel


def handler_create_project(
    name: str,
    short_description: dict[str, str] | None,
    description: dict[str, str] | None,
    level: ProjectLevel | None,
    technologies: list[str] | None,
    github_url: str | None,
    live_url: str | None,
    completed_at: date | None,
    started_at: date | None,
    is_support: bool | None,
    numeric: int | None,
    db_session: Session | None = None,
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = create_project_psql(
            name,
            short_description,
            description,
            level,
            technologies,
            github_url,
            live_url,
            completed_at,
            started_at,
            is_support,
            numeric,
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
                type_module="handler_create_project",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
