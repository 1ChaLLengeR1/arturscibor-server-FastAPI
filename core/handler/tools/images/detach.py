from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.tools.images.one import one_tool_image_psql
from core.repository.psql.tools.one import one_tool_by_id_psql
from core.repository.psql.tools.response import ToolResponse


def handler_detach_tool_image(
    tool_id: str, file_id: str, db_session: Session | None = None
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    """Odpięcie = pełne skasowanie pliku (DB + dysk) przez file domain — obraz toola
    nie ma innego zastosowania, więc nic po sobie nie zostawia (docs/3.3)."""
    try:
        _, err, ok = one_tool_by_id_psql(tool_id, db_session=db_session)
        if not ok:
            return None, err, False

        _, err, ok = one_tool_image_psql(tool_id, file_id, db_session=db_session)
        if not ok:
            return None, err, False

        _, err, ok = handler_delete_file(file_id, db_session=db_session)
        if not ok:
            return None, err, False

        return one_tool_by_id_psql(tool_id, db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_detach_tool_image",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
