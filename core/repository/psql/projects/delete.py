from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.projects import Projects


def delete_project_psql(project_id: str, db_session: Session | None = None) -> tuple[None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            project = db.execute(select(Projects).where(Projects.id == project_id)).scalar_one_or_none()
            if project is None:
                return (
                    None,
                    ApiErrorData(
                        message="Project not found",
                        type_module="delete_project_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            db.delete(project)
            db.flush()
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="delete_project_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
