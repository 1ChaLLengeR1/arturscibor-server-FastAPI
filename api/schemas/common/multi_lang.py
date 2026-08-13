from pydantic import BaseModel, ConfigDict, Field

DEFAULT_LANGUAGE_CODE = "pl"


class MultiLangText(BaseModel):
    """`pl`/`en` zawsze wymagane (gwarancja fallbacku, docs/7-i18n-section.md
    pkt. 4) — dowolny dodatkowy język przechodzi bez zmiany tego modelu, przez
    `extra="allow"` + `__pydantic_extra__`."""

    model_config = ConfigDict(extra="allow")
    __pydantic_extra__: dict[str, str]

    pl: str = Field(min_length=1)
    en: str = Field(min_length=1)
