from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.tools.response import ToolResponse, _to_tool_response
from database.psql.database import managed_session
from database.psql.models.tools import Tools


def create_tool_psql(
    name: str,
    information: str | None,
    progress: int | None,
    numeric: int | None,
    link: str | None,
    db_session: Session | None = None,
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            tool = Tools(name=name, information=information, progress=progress, numeric=numeric, link=link)
            db.add(tool)
            db.flush()
            db.refresh(tool)
            return _to_tool_response(tool), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="create_tool_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
