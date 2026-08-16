from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.one import one_project_by_id_psql
from core.repository.psql.projects.response import ProjectResponse


def handler_one_project(
    project_id: str, lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[ProjectResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = one_project_by_id_psql(project_id, lang=lang, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e), type_module="handler_one_project", type_error="exception", key_type_error="Exception"
            ),
            False,
        )
