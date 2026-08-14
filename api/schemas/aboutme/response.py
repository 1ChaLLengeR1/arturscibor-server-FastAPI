from datetime import datetime

from pydantic import BaseModel


class AboutMeImageData(BaseModel):
    file_id: str
    url: str | None
    sort_order: int


class AboutMeResponseData(BaseModel):
    id: str
    name: str | None
    job_title: str | None
    body_markdown: str | None
    images: list[AboutMeImageData]
    created_at: datetime
    updated_at: datetime
