from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.response import WorkItemResponse, _to_work_item_response
from database.psql.database import managed_session
from database.psql.models.work import EmploymentType, WorkItem

_UNSET = object()


def _apply_translatable_field(current: dict[str, str] | None, language_code: str, value: str | None) -> dict | None:
    merged = dict(current or {})
    if value is None:
        merged.pop(language_code, None)
    else:
        merged[language_code] = value
    return merged or None


def update_work_item_psql(
    work_id: str,
    item_id: str,
    language_code: str = DEFAULT_LANGUAGE_CODE,
    title: str | None = _UNSET,
    employment_type: EmploymentType | None = _UNSET,
    location: str | None = _UNSET,
    date_from: date | None = _UNSET,
    date_to: date | None = _UNSET,
    body_markdown: str | None = _UNSET,
    skills: list[str] | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[WorkItemResponse | None, ApiErrorData | None, bool]:
    """`title`/`location`/`body_markdown` edytują JEDEN język na raz
    (`language_code`, default `pl`) — docs/7-i18n-section.md pkt. 6."""
    try:
        with managed_session(db_session) as (db, _):
            item = db.execute(
                select(WorkItem).where(WorkItem.id == item_id, WorkItem.work_id == work_id)
            ).scalar_one_or_none()
            if item is None:
                return (
                    None,
                    ApiErrorData(
                        message="Work item not found",
                        type_module="update_work_item_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            if title is not _UNSET:
                if not title:
                    return (
                        None,
                        ApiErrorData(
                            message="title cannot be empty",
                            type_module="update_work_item_psql",
                            type_error="invalid_value",
                            key_type_error="InvalidValue",
                        ),
                        False,
                    )
                item.title = {**item.title, language_code: title}
            if location is not _UNSET:
                item.location = _apply_translatable_field(item.location, language_code, location)
            if body_markdown is not _UNSET:
                item.body_markdown = _apply_translatable_field(item.body_markdown, language_code, body_markdown)
            if employment_type is not _UNSET:
                item.employment_type = employment_type
            if date_from is not _UNSET:
                item.date_from = date_from
            if date_to is not _UNSET:
                item.date_to = date_to
            if skills is not _UNSET:
                item.skills = skills

            db.flush()
            db.refresh(item)
            return _to_work_item_response(item, lang=language_code), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="update_work_item_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
