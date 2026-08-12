from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.contact.delete import delete_contact_psql


def handler_delete_contact(
    id_contact: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    try:
        result, err, ok = delete_contact_psql(id_contact, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_delete_contact",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
