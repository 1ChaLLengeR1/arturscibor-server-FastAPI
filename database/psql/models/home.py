import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class CurriculumVitae(Base):
    __tablename__ = "curriculumvitae"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    path: Mapped[str | None] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String)


class Jobs(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)


class ImagesMe(Base):
    __tablename__ = "imagesme"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    path: Mapped[str | None] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String)
