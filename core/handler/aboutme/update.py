from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.aboutme.response import AboutMeResponse
from core.repository.psql.aboutme.update import _UNSET, update_about_me_psql


def handler_update_about_me(
    language_code: str = DEFAULT_LANGUAGE_CODE,
    name: str | None = _UNSET,
    job_title: str | None = _UNSET,
    body_markdown: str | None = _UNSET,
    db_session: Session | None = None,
) -> tuple[AboutMeResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = update_about_me_psql(
            language_code=language_code,
            name=name,
            job_title=job_title,
            body_markdown=body_markdown,
            db_session=db_session,
        )
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_update_about_me",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
