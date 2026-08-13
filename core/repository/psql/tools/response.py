from dataclasses import dataclass
from datetime import datetime

from database.psql.models.file import File
from database.psql.models.tools import ToolImage, Tools


@dataclass
class ToolImageResponse:
    file_id: str
    url: str | None
    sort_order: int


@dataclass
class ToolResponse:
    id: str
    name: str | None
    information: str | None
    progress: int | None
    numeric: int | None
    link: str | None
    images: list[ToolImageResponse]
    created_at: datetime
    updated_at: datetime


def _to_tool_image_response(image: ToolImage, file: File) -> ToolImageResponse:
    return ToolImageResponse(file_id=str(file.id), url=file.url, sort_order=image.sort_order)


def _to_tool_response(model: Tools, images: list[tuple[ToolImage, File]] = ()) -> ToolResponse:
    return ToolResponse(
        id=str(model.id),
        name=model.name,
        information=model.information,
        progress=model.progress,
        numeric=model.numeric,
        link=model.link,
        images=[_to_tool_image_response(image, file) for image, file in images],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
