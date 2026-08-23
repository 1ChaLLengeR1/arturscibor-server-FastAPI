from datetime import date

from pydantic import BaseModel, Field

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from database.psql.models.projects import ProjectLevel


class ProjectUpdatePayload(BaseModel):
    """Wszystkie pola opcjonalne — pominięcie zostawia dotychczasową wartość,
    jawne `null` ją czyści (poza `name` — patrz update_project_psql).
    `short_description`/`description` dotyczą jednego języka na raz, wskazanego
    przez `language_code` (docs/7-i18n-section.md pkt. 6)."""

    language_code: str = Field(default=DEFAULT_LANGUAGE_CODE, description="Który język edytujemy tym wywołaniem")
    name: str | None = Field(default=None, min_length=1, max_length=200)
    short_description: str | None = Field(default=None, max_length=280)
    description: str | None = Field(default=None, max_length=10_000)
    level: ProjectLevel | None = None
    technologies: list[str] | None = None
    github_url: str | None = Field(default=None, max_length=500)
    live_url: str | None = Field(default=None, max_length=500)
    completed_at: date | None = None
    started_at: date | None = None
    is_support: bool | None = None
    numeric: int | None = None
