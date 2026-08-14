from dataclasses import dataclass
from datetime import datetime

from database.psql.models.cv import CurriculumVitae
from database.psql.models.file import File


@dataclass
class CurriculumVitaeResponse:
    id: str
    file_id: str | None
    url: str | None
    created_at: datetime
    updated_at: datetime


def _to_cv_response(model: CurriculumVitae, file: File | None = None) -> CurriculumVitaeResponse:
    return CurriculumVitaeResponse(
        id=str(model.id),
        file_id=str(model.file_id) if model.file_id else None,
        url=file.url if file else None,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@dataclass
class CurriculumVitaeFileResponse:
    file_id: str
    directory: str
    name: str
    original_name: str
    mime_type: str | None


def _to_cv_file_response(file: File) -> CurriculumVitaeFileResponse:
    return CurriculumVitaeFileResponse(
        file_id=str(file.id),
        directory=file.directory,
        name=file.name,
        original_name=file.original_name,
        mime_type=file.mime_type,
    )
