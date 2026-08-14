from datetime import date

from pydantic import BaseModel, Field

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from database.psql.models.work import EmploymentType


class WorkItemUpdatePayload(BaseModel):
    """Wszystkie pola opcjonalne — pominięcie zostawia dotychczasową wartość.
    `title`/`location`/`body_markdown` dotyczą jednego języka na raz
    (`language_code`, docs/7-i18n-section.md pkt. 6)."""

    language_code: str = Field(default=DEFAULT_LANGUAGE_CODE, description="Który język edytujemy tym wywołaniem")
    title: str | None = Field(default=None, max_length=200)
    employment_type: EmploymentType | None = None
    location: str | None = Field(default=None, max_length=200)
    date_from: date | None = None
    date_to: date | None = None
    body_markdown: str | None = Field(default=None, max_length=20000)
    skills: list[str] | None = None
