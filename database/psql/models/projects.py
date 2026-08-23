import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class ProjectLevel(enum.StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Projects(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)  # nietłumaczalne — nazwa własna, jak Work.company_name
    # {"pl": "...", "en": "...", ...} — docs/7-i18n-section.md. pl/en zawsze obecne
    # (wymuszone przez MultiLangText na wejściu), dodatkowe języki opcjonalne.
    short_description: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    description: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    level: Mapped[ProjectLevel | None] = mapped_column(Enum(ProjectLevel, name="project_level"))
    # Nazwy technologii nietłumaczalne — zwykła lista, nie JSONB (wzorem WorkItem.skills).
    technologies: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    github_url: Mapped[str | None] = mapped_column(String)
    live_url: Mapped[str | None] = mapped_column(String)
    completed_at: Mapped[date | None] = mapped_column(Date)  # kiedy ukończony — ręczne pole domenowe, nie audyt
    started_at: Mapped[date | None] = mapped_column(Date)  # kiedy rozpoczęty — ręczne pole domenowe, jak completed_at
    is_support: Mapped[bool | None] = mapped_column(Boolean)  # czy nadal wspierany/monitorowany, czy zlecenie zamknięte
    numeric: Mapped[int | None] = mapped_column(Integer)  # kolejność wyświetlania, wzorem Tools.numeric/Work.numeric
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ProjectImage(Base):
    """Łącznik projects<->files, wzorem ToolImage/AboutMeImage (docs/3.3, docs/3.4).
    Jedna karuzela — bez podziału frontend/backend."""

    __tablename__ = "project_images"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="CASCADE"))
    # unique: jeden plik należy do co najwyżej jednego projektu.
    file_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("files.id", ondelete="CASCADE"), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
