from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.contact.response import ContactResponse, _to_contact_response
from database.psql.database import managed_session
from database.psql.models.contact import Contact

DEFAULT_LIMIT = 25


def collection_contact_psql(
    *,
    limit: int = DEFAULT_LIMIT,
    is_read: bool | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    db_session: Session | None = None,
) -> tuple[list[ContactResponse] | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            query = select(Contact)

            if is_read is not None:
                query = query.where(Contact.is_read == is_read)
            if created_from is not None:
                query = query.where(Contact.created_at >= created_from)
            if created_to is not None:
                query = query.where(Contact.created_at <= created_to)

            query = query.order_by(Contact.created_at.desc()).limit(limit)

            contacts = db.execute(query).scalars().all()
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
