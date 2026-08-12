from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import AUTH_LOGIN
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.auth.login import LoginPayload
from api.schemas.auth.response import AuthTokensData
from core.handler.auth.login import handler_login
from database.psql.database import get_db

router = APIRouter()


@router.post(
    AUTH_LOGIN,
    summary="[Public] Log in",
    response_model=ApiResponse[AuthTokensData, None],
    responses={
        401: {"model": ApiErrorResponse, "description": "Invalid login or password"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Auth"],
)
def api_login(body: LoginPayload, db: Session = Depends(get_db)) -> ApiResponse[AuthTokensData, None] | JSONResponse:
    try:
        result, error, ok = handler_login(body.login, body.password, db_session=db)
        if not ok:
            return JSONResponse(status_code=401, content=ApiErrorResponse(status_code=401, data=error).model_dump())
        return ApiResponse(status_code=200, data=AuthTokensData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_login",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
