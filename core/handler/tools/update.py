from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.tools.response import ToolResponse
from core.repository.psql.tools.update import _UNSET, update_tool_psql


def handler_update_tool(
    tool_id: str,
    name: str | None = _UNSET,
    information: str | None = _UNSET,
    progress: int | None = _UNSET,
    numeric: int | None = _UNSET,
    link: str | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = update_tool_psql(
            tool_id,
            name=name,
            information=information,
            progress=progress,
            numeric=numeric,
            link=link,
            db_session=db_session,
        )
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_update_tool", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
