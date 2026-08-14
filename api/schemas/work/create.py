from pydantic import BaseModel, Field


class WorkCreatePayload(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    numeric: int | None = Field(default=None, description="Kolejność wyświetlania firm")
