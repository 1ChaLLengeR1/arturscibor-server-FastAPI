from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.tools.delete import delete_tool_psql
from core.repository.psql.tools.one import one_tool_by_id_psql


def handler_delete_tool(tool_id: str, db_session: Session | None = None) -> tuple[None, ApiErrorData | None, bool]:
    """Kasuje tool wraz ze wszystkimi podpiętymi plikami (DB + dysk).

    Pliki kasujemy PRZED tool-em, przez ten sam handler_delete_file co zwykły
    file domain — ON DELETE CASCADE na tools_images.file_id sprząta wiersz
    łącznika przy okazji. tools_images.tool_id ma też CASCADE jako backstop,
    ale normalna ścieżka nigdy na niego nie liczy.
    """
    try:
        tool, err, ok = one_tool_by_id_psql(tool_id, db_session=db_session)
        if not ok:
            return None, err, False

        for image in tool.images:
            _, err, ok = handler_delete_file(image.file_id, db_session=db_session)
            if not ok:
                return None, err, False

        _, err, ok = delete_tool_psql(tool_id, db_session=db_session)
        if not ok:
            return None, err, False

        return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_delete_tool", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
