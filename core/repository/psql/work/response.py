from dataclasses import dataclass
from datetime import date, datetime

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from database.psql.models.file import File
from database.psql.models.work import Work, WorkItem


def _resolve_lang_text(value: dict[str, str] | None, lang: str) -> str | None:
    """Rozwiązuje JSONB {lang: text} do jednego stringa — żądany język, fallback
    na DEFAULT_LANGUAGE_CODE (docs/7-i18n-section.md pkt. 4)."""
    if not value:
        return None
    return value.get(lang) or value.get(DEFAULT_LANGUAGE_CODE)


@dataclass
class WorkItemResponse:
    id: str
    title: str | None
    employment_type: str | None
    location: str | None
    date_from: date | None
    date_to: date | None
    body_markdown: str | None
    skills: list[str] | None
    created_at: datetime
    updated_at: datetime


@dataclass
class WorkResponse:
    id: str
    company_name: str
    logo_file_id: str | None
    logo_url: str | None
    numeric: int | None
    items: list[WorkItemResponse]
    created_at: datetime
    updated_at: datetime


def _to_work_item_response(model: WorkItem, lang: str = DEFAULT_LANGUAGE_CODE) -> WorkItemResponse:
    return WorkItemResponse(
        id=str(model.id),
        title=_resolve_lang_text(model.title, lang),
        employment_type=model.employment_type.value if model.employment_type else None,
        location=_resolve_lang_text(model.location, lang),
        date_from=model.date_from,
        date_to=model.date_to,
        body_markdown=_resolve_lang_text(model.body_markdown, lang),
        skills=model.skills,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_work_response(
    model: Work,
    items: list[WorkItem] = (),
    logo_file: File | None = None,
    lang: str = DEFAULT_LANGUAGE_CODE,
) -> WorkResponse:
    return WorkResponse(
        id=str(model.id),
        company_name=model.company_name,
        logo_file_id=str(model.logo_file_id) if model.logo_file_id else None,
        logo_url=logo_file.url if logo_file else None,
        numeric=model.numeric,
        items=[_to_work_item_response(item, lang) for item in items],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
