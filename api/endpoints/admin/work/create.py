from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_WORK_CREATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.work.create import WorkCreatePayload
from api.schemas.work.response import WorkResponseData
from core.handler.work.create import handler_create_work
from database.psql.database import get_db

router = APIRouter()


@router.post(
    ADMIN_WORK_CREATE,
    summary="[Admin] Create a company (work experience entry)",
    response_model=ApiResponse[WorkResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=201,
    tags=["Admin/Work"],
)
def api_admin_create_work(
    body: WorkCreatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[WorkResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_create_work(body.company_name, body.numeric, db_session=db)
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=201, data=WorkResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_create_work", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
