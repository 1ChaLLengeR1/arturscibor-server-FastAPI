import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class EmploymentType(enum.StrEnum):
    FULL_TIME = "full_time"  # Pełny etat
    PART_TIME = "part_time"  # Niepełny etat
    CONTRACT = "contract"  # Umowa zlecenie / freelancing
    B2B = "b2b"
    INTERNSHIP = "internship"  # Staż / praktyka
    VOLUNTEER = "volunteer"  # Wolontariat


class Work(Base):
    """Firma. Logo opcjonalne, pojedyncze (wzorzec B, docs/3.4 pkt. 3) — nie karuzela."""

    __tablename__ = "work"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String)  # nietłumaczalne
    logo_file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("files.id", ondelete="SET NULL"))
    numeric: Mapped[int | None] = mapped_column(Integer)  # kolejność firm, wzorem Tools.numeric
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class WorkItem(Base):
    """Stanowisko pod firmą. `date_to = NULL` = obecnie (trwające). Sortowanie
    w obrębie firmy po `date_from DESC` — bez osobnego pola kolejności."""

    __tablename__ = "work_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    work_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("work.id", ondelete="CASCADE"))
    # {"pl": "...", "en": "...", ...} — docs/7-i18n-section.md.
    title: Mapped[dict[str, str]] = mapped_column(JSONB)
    employment_type: Mapped[EmploymentType | None] = mapped_column(Enum(EmploymentType, name="employment_type"))
    location: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    date_from: Mapped[date | None] = mapped_column(Date)
    date_to: Mapped[date | None] = mapped_column(Date)
    body_markdown: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    # Nazwy technologii nietłumaczalne — zwykła lista, nie JSONB.
    skills: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
