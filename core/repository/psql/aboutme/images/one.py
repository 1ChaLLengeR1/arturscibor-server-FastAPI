from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.aboutme import AboutMeImage


def one_about_me_image_psql(
    about_me_id: str, file_id: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            image = db.execute(
                select(AboutMeImage).where(
                    AboutMeImage.about_me_id == about_me_id, AboutMeImage.file_id == file_id
                )
            ).scalar_one_or_none()
            if image is None:
                return (
                    None,
                    ApiErrorData(
                        message="Image not attached to about me",
                        type_module="one_about_me_image_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="one_about_me_image_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
