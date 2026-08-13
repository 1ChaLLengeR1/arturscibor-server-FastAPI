from pydantic import BaseModel

from api.schemas.file.response import FileItemData, PaginationData


class FileCollectionResponseData(BaseModel):
    items: list[FileItemData]
    pagination: PaginationData
