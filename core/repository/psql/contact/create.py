from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.contact.response import ContactResponse, _to_contact_response
from database.psql.database import managed_session
from database.psql.models.contact import Contact


def create_contact_psql(
    name: str | None,
    email: str | None,
    subject: str | None,
    phone: str | None,
    description: str | None,
    db_session: Session | None = None,
) -> tuple[ContactResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            contact = Contact(name=name, email=email, subject=subject, phone=phone, description=description)
            db.add(contact)
            db.flush()
            return _to_contact_response(contact), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="create_contact_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
