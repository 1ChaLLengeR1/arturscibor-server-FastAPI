from datetime import datetime

from pydantic import BaseModel


class CurriculumVitaeResponseData(BaseModel):
    id: str
    file_id: str | None
    url: str | None
    created_at: datetime
    updated_at: datetime
