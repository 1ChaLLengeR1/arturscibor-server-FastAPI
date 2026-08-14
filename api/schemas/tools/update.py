from pydantic import BaseModel, Field

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE


class ToolUpdatePayload(BaseModel):
    """Wszystkie pola opcjonalne — endpoint wysyła do handlera tylko te, które
    faktycznie przyszły w body (model_dump(exclude_unset=True)), więc pominięcie
    pola zostawia dotychczasową wartość, a jawne `null` ją czyści (poza `name` —
    patrz update_tool_psql). `name`/`information` dotyczą jednego języka na raz,
    wskazanego przez `language_code` (docs/7-i18n-section.md pkt. 6)."""

    language_code: str = Field(default=DEFAULT_LANGUAGE_CODE, description="Który język edytujemy tym wywołaniem")
    name: str | None = Field(default=None, min_length=1, max_length=128)
    information: str | None = Field(default=None, max_length=2000)
    progress: int | None = Field(default=None, ge=0, le=100)
    numeric: int | None = None
    link: str | None = Field(default=None, max_length=500)
