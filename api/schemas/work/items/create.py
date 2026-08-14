from datetime import date

from pydantic import BaseModel

from api.schemas.common.multi_lang import MultiLangText
from database.psql.models.work import EmploymentType


class WorkItemCreatePayload(BaseModel):
    title: MultiLangText
    employment_type: EmploymentType | None = None
    location: MultiLangText | None = None
    date_from: date | None = None
    date_to: date | None = None
    body_markdown: MultiLangText | None = None
    skills: list[str] | None = None
