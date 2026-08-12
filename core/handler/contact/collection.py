from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.contact.collection import collection_contact_psql
from core.repository.psql.contact.response import ContactResponse


def handler_collection_contact(
    db_session: Session | None = None,
) -> tuple[list[ContactResponse] | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = collection_contact_psql(db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_collection_contact",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
