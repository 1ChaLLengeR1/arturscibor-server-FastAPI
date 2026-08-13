import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class CurriculumVitae(Base):
    """Singleton — dokładnie jeden wiersz, seedowany migracją, jak AboutMe.
    `file_id` nullable = brak CV, dopóki nie zostanie wgrane. Upload = podmiana
    (wzorzec B, docs/3.4-aboutme-home-section.md pkt. 3/4.4)."""

    __tablename__ = "curriculum_vitae"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("files.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
