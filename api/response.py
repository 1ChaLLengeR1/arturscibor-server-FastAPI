from pydantic import BaseModel


class ApiResponse[DATA, ADDITIONALS](BaseModel):
    status: str = "SUCCESS"
    status_code: int
    data: DATA | None = None
    additional: ADDITIONALS | None = None


class ApiErrorData(BaseModel):
    message: str
    type_module: str
    type_error: str
    key_type_error: str


class ApiErrorResponse[ADDITIONALS](BaseModel):
    status: str = "ERROR"
    status_code: int
    data: ApiErrorData
    additional: ADDITIONALS | None = None
