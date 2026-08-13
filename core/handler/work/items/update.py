from datetime import date

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.items.update import _UNSET, update_work_item_psql
from core.repository.psql.work.response import WorkItemResponse
from database.psql.models.work import EmploymentType


def handler_update_work_item(
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
    try:
        result, err, ok = update_work_item_psql(
            work_id,
            item_id,
            language_code=language_code,
            title=title,
            employment_type=employment_type,
            location=location,
            date_from=date_from,
            date_to=date_to,
            body_markdown=body_markdown,
            skills=skills,
            db_session=db_session,
        )
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_update_work_item",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
