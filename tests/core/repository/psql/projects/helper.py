from datetime import date

from sqlalchemy.orm import Session

from database.psql.models.projects import ProjectLevel, Projects

_UNSET = object()


def create_test_project(
    db: Session,
    *,
    name: str = "Portfolio API",
    short_description: dict[str, str] | None = _UNSET,
    description: dict[str, str] | None = _UNSET,
    level: ProjectLevel | None = ProjectLevel.INTERMEDIATE,
    technologies: list[str] | None = _UNSET,
    github_url: str | None = None,
    live_url: str | None = None,
    completed_at: date | None = None,
    numeric: int | None = 1,
) -> Projects:
    project = Projects(
        name=name,
        short_description=(
            {"pl": "Krótki opis", "en": "Short description"} if short_description is _UNSET else short_description
        ),
        description={"pl": "Długi opis", "en": "Long description"} if description is _UNSET else description,
        level=level,
        technologies=["Python", "FastAPI"] if technologies is _UNSET else technologies,
        github_url=github_url,
        live_url=live_url,
        completed_at=completed_at,
        numeric=numeric,
    )
    db.add(project)
    db.flush()
    return project
