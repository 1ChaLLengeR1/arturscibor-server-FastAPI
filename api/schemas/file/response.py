from datetime import datetime

from pydantic import BaseModel


class FileItemData(BaseModel):
    id: str
    original_name: str
    name: str
    size: int
    mime_type: str | None
    url: str | None
    directory: str
    file_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class PaginationData(BaseModel):
    total: int
    has_more: bool
    limit: int
    offset: int
