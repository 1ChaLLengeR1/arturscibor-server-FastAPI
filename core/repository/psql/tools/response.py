from dataclasses import dataclass
from datetime import datetime

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
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


def _resolve_lang_text(value: dict[str, str] | None, lang: str) -> str | None:
    """Rozwiązuje JSONB {lang: text} do jednego stringa — żądany język, fallback
    na DEFAULT_LANGUAGE_CODE (docs/7-i18n-section.md pkt. 4)."""
    if not value:
        return None
    return value.get(lang) or value.get(DEFAULT_LANGUAGE_CODE)


def _to_tool_response(
    model: Tools, images: list[tuple[ToolImage, File]] = (), lang: str = DEFAULT_LANGUAGE_CODE
) -> ToolResponse:
    return ToolResponse(
        id=str(model.id),
        name=_resolve_lang_text(model.name, lang),
        information=_resolve_lang_text(model.information, lang),
        progress=model.progress,
        numeric=model.numeric,
        link=model.link,
        images=[_to_tool_image_response(image, file) for image, file in images],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
