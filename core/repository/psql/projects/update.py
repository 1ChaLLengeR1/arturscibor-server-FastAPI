from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.one import _load_project_images
from core.repository.psql.projects.response import ProjectResponse, _to_project_response
from database.psql.database import managed_session
from database.psql.models.projects import ProjectLevel, Projects

_UNSET = object()


def _apply_translatable_field(current: dict[str, str] | None, language_code: str, value: str | None) -> dict | None:
    merged = dict(current or {})
    if value is None:
        merged.pop(language_code, None)
    else:
        merged[language_code] = value
    return merged or None


def update_project_psql(
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
    numeric: int | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    """`short_description`/`description` edytują JEDEN język na raz (`language_code`,
    default `pl`) w kolumnie JSONB — docs/7-i18n-section.md pkt. 6. `name` jest
    nietłumaczalne (docs/3.5-projects-section-done.md pkt. 3), edytowane niezależnie
    od `language_code`, tak jak `level`/`technologies`/`github_url`/`live_url`/
    `completed_at`/`numeric`."""
    try:
        with managed_session(db_session) as (db, _):
            project = db.execute(select(Projects).where(Projects.id == project_id)).scalar_one_or_none()
            if project is None:
                return (
                    None,
                    ApiErrorData(
                        message="Project not found",
                        type_module="update_project_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            if name is not _UNSET:
                # name jest NOT NULL w DB — jawny null odrzucamy od razu, zamiast
                # zostawiać projekt z pustą nazwą (wzorem Tools.name w update_tool_psql).
                if not name:
                    return (
                        None,
                        ApiErrorData(
                            message="name cannot be empty",
                            type_module="update_project_psql",
                            type_error="invalid_value",
                            key_type_error="InvalidValue",
                        ),
                        False,
                    )
                project.name = name
            if short_description is not _UNSET:
                project.short_description = _apply_translatable_field(
                    project.short_description, language_code, short_description
                )
            if description is not _UNSET:
                project.description = _apply_translatable_field(project.description, language_code, description)
            if level is not _UNSET:
                project.level = level
            if technologies is not _UNSET:
                project.technologies = technologies
            if github_url is not _UNSET:
                project.github_url = github_url
            if live_url is not _UNSET:
                project.live_url = live_url
            if completed_at is not _UNSET:
                project.completed_at = completed_at
            if numeric is not _UNSET:
                project.numeric = numeric

            db.flush()
            db.refresh(project)
            images = _load_project_images(db, project_id)
            return (
                _to_project_response(project, [(image, file) for image, file in images], lang=language_code),
                None,
                True,
            )
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="update_project_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
