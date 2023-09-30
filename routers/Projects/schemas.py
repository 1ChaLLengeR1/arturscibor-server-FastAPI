from pydantic import BaseModel


class DeleteProject(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True


class GetProjectId(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True


class AddTechnologyItem(BaseModel):
    id_project: str | None = None
    name: str | None = None

    class Config:
        orm_mode = True


class DeleteTechnologyId(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True


class ImageId(BaseModel):
    id: str | None = None

    class Config:
        ore_mode = True


class DwonloadProjectPath(BaseModel):
    path: str | None = None

    class Config:
        orm_mode = True
