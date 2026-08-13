from dataclasses import dataclass
from datetime import datetime

from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from database.psql.models.aboutme import AboutMe, AboutMeImage
from database.psql.models.file import File


@dataclass
class AboutMeImageResponse:
    file_id: str
    url: str | None
    sort_order: int


@dataclass
class AboutMeResponse:
    id: str
    name: str | None
    job_title: str | None
    body_markdown: str | None
    images: list[AboutMeImageResponse]
    created_at: datetime
    updated_at: datetime


def _to_about_me_image_response(image: AboutMeImage, file: File) -> AboutMeImageResponse:
    return AboutMeImageResponse(file_id=str(file.id), url=file.url, sort_order=image.sort_order)


def _resolve_lang_text(value: dict[str, str] | None, lang: str) -> str | None:
    """Rozwiązuje JSONB {lang: text} do jednego stringa — żądany język, fallback
    na DEFAULT_LANGUAGE_CODE (docs/7-i18n-section.md pkt. 4)."""
    if not value:
        return None
    return value.get(lang) or value.get(DEFAULT_LANGUAGE_CODE)


def _to_about_me_response(
    model: AboutMe, images: list[tuple[AboutMeImage, File]] = (), lang: str = DEFAULT_LANGUAGE_CODE
) -> AboutMeResponse:
    return AboutMeResponse(
        id=str(model.id),
        name=model.name,
        job_title=_resolve_lang_text(model.job_title, lang),
        body_markdown=_resolve_lang_text(model.body_markdown, lang),
        images=[_to_about_me_image_response(image, file) for image, file in images],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
