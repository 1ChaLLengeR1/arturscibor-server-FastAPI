from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from database.psql.database import managed_session
from database.psql.models.contact import Contact


def delete_contact_psql(
    id_contact: str, db_session: Session | None = None
) -> tuple[None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            contact = db.execute(select(Contact).where(Contact.id == id_contact)).scalar_one_or_none()
            if contact is None:
                return (
                    None,
                    ApiErrorData(
                        message="Contact message not found",
                        type_module="delete_contact_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            db.delete(contact)
            db.flush()
            return None, None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="delete_contact_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
