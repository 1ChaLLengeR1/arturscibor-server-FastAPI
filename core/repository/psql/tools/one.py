from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.tools.response import ToolResponse, _to_tool_response
from database.psql.database import managed_session
from database.psql.models.file import File
from database.psql.models.tools import ToolImage, Tools


def _load_tool_images(db: Session, tool_id: str) -> list[Row]:
    return db.execute(
        select(ToolImage, File)
        .join(File, File.id == ToolImage.file_id)
        .where(ToolImage.tool_id == tool_id)
        .order_by(ToolImage.sort_order)
    ).all()


def one_tool_by_id_psql(
    tool_id: str, lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[ToolResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            tool = db.execute(select(Tools).where(Tools.id == tool_id)).scalar_one_or_none()
            if tool is None:
                return (
                    None,
                    ApiErrorData(
                        message="Tool not found",
                        type_module="one_tool_by_id_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            images = _load_tool_images(db, tool_id)

            return _to_tool_response(tool, [(image, file) for image, file in images], lang=lang), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="one_tool_by_id_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
