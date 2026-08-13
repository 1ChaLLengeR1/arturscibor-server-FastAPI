from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.aboutme.response import AboutMeResponse, _to_about_me_response
from database.psql.database import managed_session
from database.psql.models.aboutme import AboutMe, AboutMeImage
from database.psql.models.file import File


def _load_about_me_images(db: Session, about_me_id) -> list[Row]:
    return db.execute(
        select(AboutMeImage, File)
        .join(File, File.id == AboutMeImage.file_id)
        .where(AboutMeImage.about_me_id == about_me_id)
        .order_by(AboutMeImage.sort_order)
    ).all()


def one_about_me_psql(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[AboutMeResponse | None, ApiErrorData | None, bool]:
    """AboutMe to singleton (docs/3.4 pkt. 4.1) — bez id parametru, zawsze
    zwraca jedyny istniejący wiersz (seedowany migracją)."""
    try:
        with managed_session(db_session) as (db, _):
            about_me = db.execute(select(AboutMe)).scalar_one_or_none()
            if about_me is None:
                return (
                    None,
                    ApiErrorData(
                        message="AboutMe not seeded",
                        type_module="one_about_me_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )

            images = _load_about_me_images(db, about_me.id)
            return _to_about_me_response(about_me, [(i, f) for i, f in images], lang=lang), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="one_about_me_psql", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
