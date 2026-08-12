import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class Contact(Base):
    __tablename__ = "contact"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)


class ImagesMessage(Base):
    __tablename__ = "imagesmessage"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_message: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("contact.id"))
    path: Mapped[str | None] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String)
