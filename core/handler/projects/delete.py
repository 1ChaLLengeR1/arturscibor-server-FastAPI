from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.projects.delete import delete_project_psql
from core.repository.psql.projects.one import one_project_by_id_psql


def handler_delete_project(
    project_id: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    """Kasuje projekt wraz ze wszystkimi podpiętymi zdjęciami (DB + dysk).

    Pliki kasujemy PRZED projektem, przez ten sam handler_delete_file co zwykły
    file domain — ON DELETE CASCADE na project_images.file_id sprząta wiersz
    łącznika przy okazji. project_images.project_id ma też CASCADE jako
    backstop, ale normalna ścieżka nigdy na niego nie liczy.
    """
    try:
        project, err, ok = one_project_by_id_psql(project_id, db_session=db_session)
        if not ok:
            return None, err, False

        for image in project.images:
            _, err, ok = handler_delete_file(image.file_id, db_session=db_session)
            if not ok:
                return None, err, False

        _, err, ok = delete_project_psql(project_id, db_session=db_session)
        if not ok:
            return None, err, False

        return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_delete_project",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
