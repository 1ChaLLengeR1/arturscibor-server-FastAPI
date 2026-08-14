from pydantic import BaseModel, Field

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE


class AboutMeUpdatePayload(BaseModel):
    """Wszystkie pola opcjonalne — endpoint wysyła do handlera tylko te, które
    faktycznie przyszły w body (model_dump(exclude_unset=True)), więc pominięcie
    pola zostawia dotychczasową wartość, a jawne `null` ją czyści. `job_title`/
    `body_markdown` dotyczą jednego języka na raz, wskazanego przez
    `language_code` (docs/7-i18n-section.md pkt. 6)."""

    language_code: str = Field(default=DEFAULT_LANGUAGE_CODE, description="Który język edytujemy tym wywołaniem")
    name: str | None = Field(default=None, max_length=128)
    job_title: str | None = Field(default=None, max_length=200)
    body_markdown: str | None = Field(default=None, max_length=20000)
