from pydantic import BaseModel, Field


class ToolCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    information: str | None = Field(default=None, max_length=2000)
    progress: int | None = Field(default=None, ge=0, le=100, description="Poziom umiejętności w %")
    numeric: int | None = Field(default=None, description="Kolejność wyświetlania")
    link: str | None = Field(default=None, max_length=500)
