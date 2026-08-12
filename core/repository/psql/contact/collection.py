from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.contact.response import ContactResponse, _to_contact_response
from database.psql.database import managed_session
from database.psql.models.contact import Contact


def collection_contact_psql(
    db_session: Session | None = None,
) -> tuple[list[ContactResponse] | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            contacts = db.execute(select(Contact).order_by(Contact.created_at.desc())).scalars().all()
            return [_to_contact_response(contact) for contact in contacts], None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="collection_contact_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
