from sqlalchemy.orm import Session

from api.response import ApiErrorData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from core.repository.psql.projects.collection import collection_projects_psql
from core.repository.psql.projects.response import ProjectResponse


def handler_collection_projects(
    lang: str = DEFAULT_LANGUAGE_CODE, db_session: Session | None = None
) -> tuple[list[ProjectResponse] | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = collection_projects_psql(lang=lang, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_collection_projects",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
