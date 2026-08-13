from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.tools import Tools


def delete_tool_psql(tool_id: str, db_session: Session | None = None) -> tuple[None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            tool = db.execute(select(Tools).where(Tools.id == tool_id)).scalar_one_or_none()
            if tool is None:
                return (
                    None,
                    ApiErrorData(
                        message="Tool not found",
                        type_module="delete_tool_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            db.delete(tool)
            db.flush()
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="delete_tool_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
