from datetime import datetime

from pydantic import BaseModel


class ToolImageData(BaseModel):
    file_id: str
    url: str | None
    sort_order: int


class ToolResponseData(BaseModel):
    id: str
    name: str | None
    information: str | None
    progress: int | None
    numeric: int | None
    link: str | None
    images: list[ToolImageData]
    created_at: datetime
    updated_at: datetime
