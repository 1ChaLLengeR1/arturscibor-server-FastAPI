from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.tools.one import _load_tool_images
from core.repository.psql.tools.response import ToolResponse, _to_tool_response
from database.psql.database import managed_session
from database.psql.models.tools import Tools

_UNSET = object()


def update_tool_psql(
    tool_id: str,
    name: str | None = _UNSET,
    information: str | None = _UNSET,
    progress: int | None = _UNSET,
    numeric: int | None = _UNSET,
    link: str | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            tool = db.execute(select(Tools).where(Tools.id == tool_id)).scalar_one_or_none()
            if tool is None:
                return (
                    None,
                    ApiErrorData(
                        message="Tool not found",
                        type_module="update_tool_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            if name is not _UNSET:
                tool.name = name
            if information is not _UNSET:
                tool.information = information
            if progress is not _UNSET:
                tool.progress = progress
            if numeric is not _UNSET:
                tool.numeric = numeric
            if link is not _UNSET:
                tool.link = link

            db.flush()
            db.refresh(tool)
            images = _load_tool_images(db, tool_id)
            return _to_tool_response(tool, [(image, file) for image, file in images]), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="update_tool_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
