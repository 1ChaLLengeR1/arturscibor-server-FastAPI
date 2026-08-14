import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class AboutMe(Base):
    """Singleton — dokładnie jeden wiersz, seedowany migracją. Bez create/delete,
    tylko get (publiczny) + update (admin) — docs/3.4-aboutme-home-section.md pkt. 4.1."""

    __tablename__ = "about_me"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)  # nietłumaczalne
    # {"pl": "...", "en": "...", ...} — docs/7-i18n-section.md.
    job_title: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    body_markdown: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AboutMeImage(Base):
    """Łącznik about_me<->files, wzorem ToolImage (docs/3.3-tools-section-done.md)."""

    __tablename__ = "about_me_images"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    about_me_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("about_me.id", ondelete="CASCADE"))
    file_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("files.id", ondelete="CASCADE"), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
