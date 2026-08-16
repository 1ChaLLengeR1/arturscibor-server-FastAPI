from dataclasses import dataclass
from datetime import date, datetime

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from database.psql.models.file import File
from database.psql.models.projects import ProjectImage, Projects


def _resolve_lang_text(value: dict[str, str] | None, lang: str) -> str | None:
    """Rozwiązuje JSONB {lang: text} do jednego stringa — żądany język, fallback
    na DEFAULT_LANGUAGE_CODE (docs/7-i18n-section.md pkt. 4)."""
    if not value:
        return None
    return value.get(lang) or value.get(DEFAULT_LANGUAGE_CODE)


@dataclass
class ProjectImageResponse:
    file_id: str
    url: str | None
    sort_order: int


@dataclass
class ProjectResponse:
    id: str
    name: str
    short_description: str | None
    description: str | None
    level: str | None
    technologies: list[str]
    github_url: str | None
    live_url: str | None
    completed_at: date | None
    numeric: int | None
    images: list[ProjectImageResponse]
    created_at: datetime
    updated_at: datetime


def _to_project_image_response(image: ProjectImage, file: File) -> ProjectImageResponse:
    return ProjectImageResponse(file_id=str(file.id), url=file.url, sort_order=image.sort_order)


def _to_project_response(
    model: Projects, images: list[tuple[ProjectImage, File]] = (), lang: str = DEFAULT_LANGUAGE_CODE
) -> ProjectResponse:
    return ProjectResponse(
        id=str(model.id),
        name=model.name,
        short_description=_resolve_lang_text(model.short_description, lang),
        description=_resolve_lang_text(model.description, lang),
        level=model.level.value if model.level else None,
        technologies=model.technologies or [],
        github_url=model.github_url,
        live_url=model.live_url,
        completed_at=model.completed_at,
        numeric=model.numeric,
        images=[_to_project_image_response(image, file) for image, file in images],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
