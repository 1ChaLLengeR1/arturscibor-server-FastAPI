from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.response import ProjectResponse, _to_project_response
from database.psql.database import managed_session
from database.psql.models.file import File
from database.psql.models.projects import ProjectImage, Projects


def collection_projects_psql(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[list[ProjectResponse] | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            query = select(Projects).order_by(Projects.numeric.asc().nulls_last(), Projects.created_at)
            projects = db.execute(query).scalars().all()

            images_by_project = defaultdict(list)
            if projects:
                rows = db.execute(
                    select(ProjectImage, File)
                    .join(File, File.id == ProjectImage.file_id)
                    .where(ProjectImage.project_id.in_([project.id for project in projects]))
                    .order_by(ProjectImage.sort_order)
                ).all()
                for image, file in rows:
                    images_by_project[image.project_id].append((image, file))

            return (
                [_to_project_response(project, images_by_project[project.id], lang=lang) for project in projects],
                None,
                True,
            )
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="collection_projects_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
