from datetime import date

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.response import ProjectResponse, _to_project_response
from database.psql.database import managed_session
from database.psql.models.projects import ProjectLevel, Projects


def create_project_psql(
    name: str,
    short_description: dict[str, str] | None,
    description: dict[str, str] | None,
    level: ProjectLevel | None,
    technologies: list[str] | None,
    github_url: str | None,
    live_url: str | None,
    completed_at: date | None,
    numeric: int | None,
    db_session: Session | None = None,
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            project = Projects(
                name=name,
                short_description=short_description,
                description=description,
                level=level,
                technologies=technologies,
                github_url=github_url,
                live_url=live_url,
                completed_at=completed_at,
                numeric=numeric,
            )
            db.add(project)
            db.flush()
            db.refresh(project)
            return _to_project_response(project, lang=DEFAULT_LANGUAGE_CODE), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="create_project_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
