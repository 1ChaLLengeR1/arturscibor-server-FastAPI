from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.response import ProjectResponse, _to_project_response
from database.psql.database import managed_session
from database.psql.models.file import File
from database.psql.models.projects import ProjectImage, Projects


def _load_project_images(db: Session, project_id: str) -> list[Row]:
    return db.execute(
        select(ProjectImage, File)
        .join(File, File.id == ProjectImage.file_id)
        .where(ProjectImage.project_id == project_id)
        .order_by(ProjectImage.sort_order)
    ).all()


def one_project_by_id_psql(
    project_id: str, lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            project = db.execute(select(Projects).where(Projects.id == project_id)).scalar_one_or_none()
            if project is None:
                return (
                    None,
                    ApiErrorData(
                        message="Project not found",
                        type_module="one_project_by_id_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            images = _load_project_images(db, project_id)

            return _to_project_response(project, [(image, file) for image, file in images], lang=lang), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="one_project_by_id_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
