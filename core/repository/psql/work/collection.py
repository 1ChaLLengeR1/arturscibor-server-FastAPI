from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.one import _load_work_items, _load_work_logo
from core.repository.psql.work.response import WorkResponse, _to_work_response
from database.psql.database import managed_session
from database.psql.models.work import Work


def collection_work_psql(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[list[WorkResponse] | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            query = select(Work).order_by(Work.numeric.asc().nulls_last(), Work.created_at)
            companies = db.execute(query).scalars().all()

            result = []
            for company in companies:
                items = _load_work_items(db, company.id)
                logo_file = _load_work_logo(db, company)
                result.append(_to_work_response(company, items, logo_file, lang=lang))
            return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="collection_work_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
