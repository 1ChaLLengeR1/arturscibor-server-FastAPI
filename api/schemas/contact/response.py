from datetime import datetime

from pydantic import BaseModel


class ContactResponseData(BaseModel):
    id: str
    name: str | None
    email: str | None
    subject: str | None
    phone: str | None
    description: str | None
    is_read: bool
    created_at: datetime
    updated_at: datetime
