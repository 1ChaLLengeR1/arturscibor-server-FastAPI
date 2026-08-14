from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.aboutme.images.attach import attach_about_me_image_psql
from core.repository.psql.aboutme.one import one_about_me_psql
from core.repository.psql.aboutme.response import AboutMeResponse
from core.repository.psql.file.one import one_file_by_id_psql
from database.psql.models.file import FileStatus


def handler_attach_about_me_image(
    file_id: str, db_session: Session | None = None
) -> tuple[AboutMeResponse | None, ApiErrorData | None, bool]:
    try:
        about_me, err, ok = one_about_me_psql(db_session=db_session)
        if not ok:
            return None, err, False

        file, err, ok = one_file_by_id_psql(file_id, db_session=db_session)
        if not ok:
            return None, err, False

        if file.status != FileStatus.CONFIRMED.value:
            return (
                None,
                ApiErrorData(
                    message=f"File must be confirmed before it can be attached (current: {file.status})",
                    type_module="handler_attach_about_me_image",
                    type_error="invalid_status",
                    key_type_error="InvalidStatus",
                ),
                False,
            )

        _, err, ok = attach_about_me_image_psql(
            about_me.id, file_id, sort_order=len(about_me.images), db_session=db_session
        )
        if not ok:
            return None, err, False

        return one_about_me_psql(db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_attach_about_me_image",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
