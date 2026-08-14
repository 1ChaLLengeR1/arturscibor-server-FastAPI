from datetime import date, datetime

from pydantic import BaseModel


class WorkItemResponseData(BaseModel):
    id: str
    title: str | None
    employment_type: str | None
    location: str | None
    date_from: date | None
    date_to: date | None
    body_markdown: str | None
    skills: list[str] | None
    created_at: datetime
    updated_at: datetime


class WorkResponseData(BaseModel):
    id: str
    company_name: str
    logo_file_id: str | None
    logo_url: str | None
    numeric: int | None
    items: list[WorkItemResponseData]
    created_at: datetime
    updated_at: datetime
