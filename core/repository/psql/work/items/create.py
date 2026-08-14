from datetime import date

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.response import WorkItemResponse, _to_work_item_response
from database.psql.database import managed_session
from database.psql.models.work import EmploymentType, WorkItem


def create_work_item_psql(
    work_id: str,
    title: dict[str, str],
    employment_type: EmploymentType | None,
    location: dict[str, str] | None,
    date_from: date | None,
    date_to: date | None,
    body_markdown: dict[str, str] | None,
    skills: list[str] | None,
    db_session: Session | None = None,
) -> tuple[WorkItemResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            item = WorkItem(
                work_id=work_id,
                title=title,
                employment_type=employment_type,
                location=location,
                date_from=date_from,
                date_to=date_to,
                body_markdown=body_markdown,
                skills=skills,
            )
            db.add(item)
            db.flush()
            db.refresh(item)
            return _to_work_item_response(item, lang=DEFAULT_LANGUAGE_CODE), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="create_work_item_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
