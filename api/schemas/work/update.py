from pydantic import BaseModel, Field


class WorkUpdatePayload(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=200)
    numeric: int | None = None
