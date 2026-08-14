import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class FileStatus(enum.StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFIRMED = "confirmed"


class FileType(enum.StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"  # CV — docs/3.4-aboutme-home-section.md pkt. 4.4


# "work" (logo firm) i "cv" dopisane przy okazji domen work/cv — docs/3.4 pkt. 4.3.
# "work" był potrzebny już wcześniej (logo firmy), a został tu przeoczony przy
# implementacji work — naprawione teraz, żeby testy logo faktycznie przechodziły.
ALLOWED_DIRECTORIES: set[str] = {"projects", "aboutme", "tools", "work", "cv"}

ALLOWED_EXTENSIONS: dict[FileType, set[str]] = {
    FileType.PHOTO: {".jpg", ".jpeg", ".png", ".webp"},
    FileType.VIDEO: {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"},
    FileType.DOCUMENT: {".pdf"},
}

MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    original_name: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, unique=True)
    size: Mapped[int] = mapped_column(BigInteger)
    mime_type: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)

    directory: Mapped[str] = mapped_column(String)
    file_type: Mapped[FileType] = mapped_column(Enum(FileType, name="file_type"))
    status: Mapped[FileStatus] = mapped_column(Enum(FileStatus, name="file_status"), default=FileStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_files_status", "status"),
        Index("ix_files_file_type", "file_type"),
        Index("ix_files_directory", "directory"),
    )
