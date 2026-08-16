from datetime import date

from pydantic import BaseModel, Field

from api.schemas.common.multi_lang import MultiLangText
from database.psql.models.projects import ProjectLevel


class ProjectCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    short_description: MultiLangText | None = None
    description: MultiLangText | None = None
    level: ProjectLevel | None = None
    technologies: list[str] | None = None
    github_url: str | None = Field(default=None, max_length=500)
    live_url: str | None = Field(default=None, max_length=500)
    completed_at: date | None = None
    numeric: int | None = Field(default=None, description="Kolejność wyświetlania")
