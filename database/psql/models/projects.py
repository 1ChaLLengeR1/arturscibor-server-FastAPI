import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class Projects(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name_project: Mapped[str | None] = mapped_column(String)
    short_description: Mapped[str | None] = mapped_column(String)
    file_path: Mapped[str | None] = mapped_column(String)
    file_link: Mapped[str | None] = mapped_column(String)
    completion_data: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    project_number: Mapped[int | None] = mapped_column(Integer)
    level_advanced: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    link_page: Mapped[str | None] = mapped_column(String)


class FileProjects(Base):
    __tablename__ = "filesproject"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_project: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("projects.id"))
    name: Mapped[str | None] = mapped_column(String)
    path: Mapped[str | None] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String)


class ImagesProjects(Base):
    __tablename__ = "imagesproject"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_project: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("projects.id"))
    name: Mapped[str | None] = mapped_column(String)
    path: Mapped[str | None] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String)


class TechnologiesProject(Base):
    __tablename__ = "technologiesproject"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_project: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("projects.id"))
    name: Mapped[str | None] = mapped_column(String)
