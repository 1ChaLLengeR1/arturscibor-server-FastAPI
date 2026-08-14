from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.work.response import WorkResponse, _to_work_response
from database.psql.database import managed_session
from database.psql.models.file import File
from database.psql.models.work import Work, WorkItem


def _load_work_items(db: Session, work_id) -> list[WorkItem]:
    query = select(WorkItem).where(WorkItem.work_id == work_id).order_by(WorkItem.date_from.desc().nulls_last())
    return db.execute(query).scalars().all()


def _load_work_logo(db: Session, work: Work) -> File | None:
    if work.logo_file_id is None:
        return None
    return db.execute(select(File).where(File.id == work.logo_file_id)).scalar_one_or_none()


def one_work_by_id_psql(
    work_id: str, lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[WorkResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            work = db.execute(select(Work).where(Work.id == work_id)).scalar_one_or_none()
            if work is None:
                return (
                    None,
                    ApiErrorData(
                        message="Work not found",
                        type_module="one_work_by_id_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            items = _load_work_items(db, work_id)
            logo_file = _load_work_logo(db, work)
            return _to_work_response(work, items, logo_file, lang=lang), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="one_work_by_id_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
