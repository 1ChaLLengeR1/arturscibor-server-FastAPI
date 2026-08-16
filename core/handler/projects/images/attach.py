from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.one import one_file_by_id_psql
from core.repository.psql.projects.images.attach import attach_project_image_psql
from core.repository.psql.projects.one import one_project_by_id_psql
from core.repository.psql.projects.response import ProjectResponse
from database.psql.models.file import FileStatus


def handler_attach_project_image(
    project_id: str, file_id: str, db_session: Session | None = None
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    try:
        project, err, ok = one_project_by_id_psql(project_id, db_session=db_session)
        if not ok:
            return None, err, False

        file, err, ok = one_file_by_id_psql(file_id, db_session=db_session)
        if not ok:
            return None, err, False

        if file.status != FileStatus.CONFIRMED.value:
            return (
                None,
                ApiErrorData(
                    message=f"File must be confirmed before it can be attached (current: {file.status})",
                    type_module="handler_attach_project_image",
                    type_error="invalid_status",
                    key_type_error="InvalidStatus",
                ),
                False,
            )

        _, err, ok = attach_project_image_psql(
            project_id, file_id, sort_order=len(project.images), db_session=db_session
        )
        if not ok:
            return None, err, False

        return one_project_by_id_psql(project_id, db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_attach_project_image",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
