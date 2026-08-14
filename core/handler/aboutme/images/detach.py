from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.handler.file.delete import handler_delete_file
from core.repository.psql.aboutme.images.one import one_about_me_image_psql
from core.repository.psql.aboutme.one import one_about_me_psql
from core.repository.psql.aboutme.response import AboutMeResponse


def handler_detach_about_me_image(
    file_id: str, db_session: Session | None = None
) -> tuple[AboutMeResponse | None, ApiErrorData | None, bool]:
    """Odpięcie = pełne skasowanie pliku (DB + dysk) przez file domain, jak w tools."""
    try:
        about_me, err, ok = one_about_me_psql(db_session=db_session)
        if not ok:
            return None, err, False

        _, err, ok = one_about_me_image_psql(about_me.id, file_id, db_session=db_session)
        if not ok:
            return None, err, False

        _, err, ok = handler_delete_file(file_id, db_session=db_session)
        if not ok:
            return None, err, False

        return one_about_me_psql(db_session=db_session)
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_detach_about_me_image",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
