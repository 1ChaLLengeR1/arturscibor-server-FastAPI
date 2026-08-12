import uuid

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class Information(Base):
    __tablename__ = "informationme"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    information: Mapped[str | None] = mapped_column(String)


class AboutMe(Base):
    __tablename__ = "aboutme"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    job: Mapped[str | None] = mapped_column(String)
    information: Mapped[str | None] = mapped_column(String)
    path_image: Mapped[str | None] = mapped_column(String)
    link_image: Mapped[str | None] = mapped_column(String)


class ReadMore(Base):
    __tablename__ = "readmore"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    information: Mapped[str | None] = mapped_column(String)
    numeric: Mapped[int | None] = mapped_column(Integer)
