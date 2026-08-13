from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.tools.collection import collection_tools_psql
from core.repository.psql.tools.response import ToolResponse


def handler_collection_tools(
    db_session: Session | None = None,
) -> tuple[list[ToolResponse] | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = collection_tools_psql(db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_collection_tools",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
