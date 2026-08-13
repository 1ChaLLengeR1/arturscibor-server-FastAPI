from pydantic import BaseModel, Field


class ToolUpdatePayload(BaseModel):
    """Wszystkie pola opcjonalne — endpoint wysyła do handlera tylko te, które
    faktycznie przyszły w body (model_dump(exclude_unset=True)), więc pominięcie
    pola zostawia dotychczasową wartość, a jawne `null` ją czyści."""

    name: str | None = Field(default=None, min_length=1, max_length=128)
    information: str | None = Field(default=None, max_length=2000)
    progress: int | None = Field(default=None, ge=0, le=100)
    numeric: int | None = None
    link: str | None = Field(default=None, max_length=500)
