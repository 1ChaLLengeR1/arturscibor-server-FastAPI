from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.tools.response import ToolResponse, _to_tool_response
from database.psql.database import managed_session
from database.psql.models.file import File
from database.psql.models.tools import ToolImage, Tools


def collection_tools_psql(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[list[ToolResponse] | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            query = select(Tools).order_by(Tools.numeric.asc().nulls_last(), Tools.created_at)
            tools = db.execute(query).scalars().all()

            images_by_tool = defaultdict(list)
            if tools:
                rows = db.execute(
                    select(ToolImage, File)
                    .join(File, File.id == ToolImage.file_id)
                    .where(ToolImage.tool_id.in_([tool.id for tool in tools]))
                    .order_by(ToolImage.sort_order)
                ).all()
                for image, file in rows:
                    images_by_tool[image.tool_id].append((image, file))

            return [_to_tool_response(tool, images_by_tool[tool.id], lang=lang) for tool in tools], None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="collection_tools_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
