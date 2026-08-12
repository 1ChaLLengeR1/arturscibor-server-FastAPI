from sqlalchemy.orm import Session

from database.psql.models.contact import Contact


def create_test_contact(
    db: Session,
    *,
    name: str = "Test User",
    email: str = "test@example.com",
    subject: str | None = None,
    phone: str | None = None,
    description: str = "Test message",
) -> Contact:
    contact = Contact(name=name, email=email, subject=subject, phone=phone, description=description)
    db.add(contact)
    db.flush()
    return contact
