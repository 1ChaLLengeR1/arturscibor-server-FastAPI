from datetime import date

from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.work.items.create import create_work_item_psql
from core.repository.psql.work.one import one_work_by_id_psql
from core.repository.psql.work.response import WorkItemResponse
from database.psql.models.work import EmploymentType


def handler_create_work_item(
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
        _, err, ok = one_work_by_id_psql(work_id, db_session=db_session)
        if not ok:
            return None, err, False

        result, err, ok = create_work_item_psql(
            work_id,
            title,
            employment_type,
            location,
            date_from,
            date_to,
            body_markdown,
            skills,
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
                type_module="handler_create_work_item",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
