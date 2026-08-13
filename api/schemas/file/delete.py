from pydantic import BaseModel


class DeleteFileResponseData(BaseModel):
    deleted: bool
    id: str
