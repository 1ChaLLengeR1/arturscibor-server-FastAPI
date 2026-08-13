from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.aboutme.one import one_about_me_psql
from core.repository.psql.aboutme.response import AboutMeResponse


def handler_get_about_me(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[AboutMeResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = one_about_me_psql(lang=lang, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_get_about_me", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
