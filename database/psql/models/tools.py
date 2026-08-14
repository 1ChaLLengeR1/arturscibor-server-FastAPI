import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class Tools(Base):
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # {"pl": "...", "en": "...", ...} — docs/7-i18n-section.md. pl/en zawsze obecne
    # (wymuszone przez MultiLangText na wejściu), dodatkowe języki opcjonalne.
    name: Mapped[dict[str, str]] = mapped_column(JSONB)
    information: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    progress: Mapped[int | None] = mapped_column(Integer)
    numeric: Mapped[int | None] = mapped_column(Integer)
    link: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ToolImage(Base):
    """Łącznik tools<->files (docs/6-file-storage-section-done.md) — `File` zostaje
    domenowo-neutralny, ownership żyje tutaj, wzorem starego ImagesProjects.id_project.
    """

    __tablename__ = "tools_images"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tool_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tools.id", ondelete="CASCADE"))
    # unique: jeden plik należy do co najwyżej jednego toola.
    file_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("files.id", ondelete="CASCADE"), unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
