from datetime import date, datetime

from pydantic import BaseModel


class ProjectImageData(BaseModel):
    file_id: str
    url: str | None
    sort_order: int


class ProjectResponseData(BaseModel):
    id: str
    name: str
    short_description: str | None
    description: str | None
    level: str | None
    technologies: list[str]
    github_url: str | None
    live_url: str | None
    completed_at: date | None
    started_at: date | None
    is_support: bool | None
    numeric: int | None
    images: list[ProjectImageData]
    created_at: datetime
    updated_at: datetime
