from dataclasses import dataclass, field
from datetime import datetime

from database.psql.models.file import File


@dataclass
class FileResponse:
    id: str
    original_name: str
    name: str
    size: int
    mime_type: str | None
    url: str | None
    directory: str
    file_type: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass
class FileCollectionResponse:
    items: list[FileResponse] = field(default_factory=list)
    total: int = 0


@dataclass
class FileInitResponse:
    file_id: str
    upload_url: str
    public_url: str


@dataclass
class DeleteFileResponse:
    deleted: bool
    id: str
    directory: str
    name: str


def _to_file_response(model: File) -> FileResponse:
    return FileResponse(
        id=str(model.id),
        original_name=model.original_name,
        name=model.name,
        size=model.size,
        mime_type=model.mime_type,
        url=model.url,
        directory=model.directory,
        file_type=model.file_type.value,
        status=model.status.value,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
