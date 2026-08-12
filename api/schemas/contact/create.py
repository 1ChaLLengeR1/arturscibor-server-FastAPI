from pydantic import BaseModel, EmailStr, Field


class ContactCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    email: EmailStr
    subject: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)
    description: str = Field(min_length=1, max_length=2000)
