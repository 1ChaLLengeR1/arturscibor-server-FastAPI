import uuid

from sqlalchemy.orm import Session

from database.psql.models.file import File, FileStatus, FileType


def create_test_file(
    db: Session,
    *,
    original_name: str = "test.png",
    name: str | None = None,
    size: int = 1024,
    directory: str = "projects",
    file_type: FileType = FileType.PHOTO,
    mime_type: str = "image/png",
    status: FileStatus = FileStatus.PENDING,
) -> File:
    file = File(
        original_name=original_name,
        name=name or f"{uuid.uuid4().hex[:8]}_{original_name}",
        size=size,
        directory=directory,
        file_type=file_type,
        mime_type=mime_type,
        status=status,
    )
    db.add(file)
    db.flush()
    return file
