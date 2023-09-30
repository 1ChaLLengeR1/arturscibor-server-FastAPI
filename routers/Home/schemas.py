from pydantic import BaseModel


class HomePostJobs(BaseModel):
    id: str | None = None
    job: str

    class Config:
        orm_mode = True


class HomeDeleteJobs(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True


class InformationMe(BaseModel):
    id: str | None = None
    information: str | None = None

    class Config:
        orm_mode = True


class HomeDeleteImageMe(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True


