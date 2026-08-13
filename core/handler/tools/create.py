from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.tools.create import create_tool_psql
from core.repository.psql.tools.response import ToolResponse


def handler_create_tool(
    name: str,
    information: str | None,
    progress: int | None,
    numeric: int | None,
    link: str | None,
    db_session: Session | None = None,
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = create_tool_psql(name, information, progress, numeric, link, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_create_tool", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
