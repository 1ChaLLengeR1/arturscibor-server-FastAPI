from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.contact.create import create_contact_psql
from core.repository.psql.contact.response import ContactResponse


def handler_create_contact(
    name: str | None,
    email: str | None,
    subject: str | None,
    phone: str | None,
    description: str | None,
    db_session: Session | None = None,
) -> tuple[ContactResponse | None, ApiErrorData | None, bool]:
    try:
        result, err, ok = create_contact_psql(name, email, subject, phone, description, db_session=db_session)
        if not ok:
            return None, err, False
        return result, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_create_contact",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
