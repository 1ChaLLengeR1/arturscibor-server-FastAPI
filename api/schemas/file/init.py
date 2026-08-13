from pydantic import BaseModel, Field

from database.psql.models.file import ALLOWED_DIRECTORIES, FileType


class FileInitPayload(BaseModel):
    # max_length = szerokość kolumny files.original_name; bez tego dłuższa nazwa
    # przechodziła do INSERT-a i wracała jako 500 (DataError) zamiast 422.
    original_name: str = Field(
        min_length=1, max_length=255, description="Oryginalna nazwa pliku z rozszerzeniem"
    )
    size: int = Field(gt=0, description="Rozmiar pliku w bajtach")
    directory: str = Field(description=f"Katalog docelowy: {sorted(ALLOWED_DIRECTORIES)}")
    file_type: FileType = Field(description="Typ pliku: photo | video")
    mime_type: str | None = Field(default=None, description="MIME type, np. image/png")


class FileInitResponseData(BaseModel):
    file_id: str
    upload_url: str
    public_url: str
