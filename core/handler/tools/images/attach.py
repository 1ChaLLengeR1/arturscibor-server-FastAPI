from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.file.one import one_file_by_id_psql
from core.repository.psql.tools.images.attach import attach_tool_image_psql
from core.repository.psql.tools.one import one_tool_by_id_psql
from core.repository.psql.tools.response import ToolResponse
from database.psql.models.file import FileStatus


def handler_attach_tool_image(
    tool_id: str, file_id: str, db_session: Session | None = None
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    try:
        tool, err, ok = one_tool_by_id_psql(tool_id, db_session=db_session)
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
                    type_module="handler_attach_tool_image",
                    type_error="invalid_status",
                    key_type_error="InvalidStatus",
                ),
                False,
            )

        _, err, ok = attach_tool_image_psql(tool_id, file_id, sort_order=len(tool.images), db_session=db_session)
        if not ok:
            return None, err, False

        return one_tool_by_id_psql(tool_id, db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_attach_tool_image",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
