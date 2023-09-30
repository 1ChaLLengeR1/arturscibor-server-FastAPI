from pydantic import BaseModel


class ReadMoreAddItem(BaseModel):
    name: str | None = None
    information: str | None = None
    numeric: int | None = None

    class Config:
        orm_mode: True


class ReadMoreUpdateItem(BaseModel):
    id: str | None = None
    name: str | None = None
    information: str | None = None
    numeric: int | None = None

    class Config:
        orm_mode: True


class ReadMoreId(BaseModel):
    id: str | None = None

    class Config:
        orm_mode: True
