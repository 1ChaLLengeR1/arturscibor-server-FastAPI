from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.aboutme.one import _load_about_me_images
from core.repository.psql.aboutme.response import AboutMeResponse, _to_about_me_response
from database.psql.database import managed_session
from database.psql.models.aboutme import AboutMe

_UNSET = object()


def _apply_translatable_field(current: dict[str, str] | None, language_code: str, value: str | None) -> dict | None:
    merged = dict(current or {})
    if value is None:
        merged.pop(language_code, None)
    else:
        merged[language_code] = value
    return merged or None


def update_about_me_psql(
    language_code: str = DEFAULT_LANGUAGE_CODE,
    name: str | None = _UNSET,
    job_title: str | None = _UNSET,
    body_markdown: str | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[AboutMeResponse | None, ApiErrorData | None, bool]:
    """`job_title`/`body_markdown` edytują JEDEN język na raz (`language_code`,
    default `pl`) w kolumnie JSONB — docs/7-i18n-section.md pkt. 6. `name` jest
    nietłumaczalne, edytowane niezależnie od `language_code`."""
    try:
        with managed_session(db_session) as (db, _):
            about_me = db.execute(select(AboutMe)).scalar_one_or_none()
            if about_me is None:
                return (
                    None,
                    ApiErrorData(
                        message="AboutMe not seeded",
                        type_module="update_about_me_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            if name is not _UNSET:
                about_me.name = name
            if job_title is not _UNSET:
                about_me.job_title = _apply_translatable_field(about_me.job_title, language_code, job_title)
            if body_markdown is not _UNSET:
                about_me.body_markdown = _apply_translatable_field(
                    about_me.body_markdown, language_code, body_markdown
                )

            db.flush()
            db.refresh(about_me)
            images = _load_about_me_images(db, about_me.id)
            return (
                _to_about_me_response(about_me, [(i, f) for i, f in images], lang=language_code),
                None,
                True,
            )
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="update_about_me_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
