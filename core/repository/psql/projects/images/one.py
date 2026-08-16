from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.projects import ProjectImage


def one_project_image_psql(
    project_id: str, file_id: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    """Sprawdza, że `file_id` jest podpięty pod `project_id` — używane przez
    detach, żeby odróżnić "plik nie istnieje" (404 z file domain) od "plik
    istnieje, ale nie jest podpięty pod TEN projekt" (404 tutaj)."""
    try:
        with managed_session(db_session) as (db, _):
            image = db.execute(
                select(ProjectImage).where(ProjectImage.project_id == project_id, ProjectImage.file_id == file_id)
            ).scalar_one_or_none()
            if image is None:
                return (
                    None,
                    ApiErrorData(
                        message="Image not attached to this project",
                        type_module="one_project_image_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="one_project_image_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
