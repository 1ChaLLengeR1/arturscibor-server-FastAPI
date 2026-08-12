from dataclasses import dataclass
from datetime import datetime

from database.psql.models.contact import Contact


@dataclass
class ContactResponse:
    id: str
    name: str | None
    email: str | None
    subject: str | None
    phone: str | None
    description: str | None
    is_read: bool
    created_at: datetime
    updated_at: datetime


def _to_contact_response(model: Contact) -> ContactResponse:
    return ContactResponse(
        id=str(model.id),
        name=model.name,
        email=model.email,
        subject=model.subject,
        phone=model.phone,
        description=model.description,
        is_read=model.is_read,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
