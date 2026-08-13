import uuid
from datetime import date

from sqlalchemy.orm import Session

from database.psql.models.work import EmploymentType, WorkItem


def create_test_work_item(
    db: Session,
    work_id: uuid.UUID | str,
    *,
    title: dict[str, str] | None = None,
    employment_type: EmploymentType | None = EmploymentType.FULL_TIME,
    location: dict[str, str] | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    body_markdown: dict[str, str] | None = None,
    skills: list[str] | None = None,
) -> WorkItem:
    item = WorkItem(
        work_id=work_id,
        title=title or {"pl": "Software Engineer", "en": "Software Engineer"},
        employment_type=employment_type,
        location=location,
        date_from=date_from,
        date_to=date_to,
        body_markdown=body_markdown,
        skills=skills,
    )
    db.add(item)
    db.flush()
    return item
