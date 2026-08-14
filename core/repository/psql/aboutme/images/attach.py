from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.aboutme import AboutMeImage


def attach_about_me_image_psql(
    about_me_id: str, file_id: str, sort_order: int, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            db.add(AboutMeImage(about_me_id=about_me_id, file_id=file_id, sort_order=sort_order))
            try:
                db.flush()
            except IntegrityError:
                db.rollback()
                return (
                    None,
                    ApiErrorData(
                        message="File is already attached to about me",
                        type_module="attach_about_me_image_psql",
                        type_error="conflict",
                        key_type_error="AlreadyAttached",
                    ),
                    False,
                )
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="attach_about_me_image_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
