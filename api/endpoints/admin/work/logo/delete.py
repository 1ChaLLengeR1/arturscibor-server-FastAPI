from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_WORK_LOGO
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.work.response import WorkResponseData
from api.status import STATUS_BY_KEY
from core.handler.work.logo.delete import handler_delete_work_logo
from database.psql.database import get_db

router = APIRouter()


@router.delete(
    ADMIN_WORK_LOGO,
    summary="[Admin] Remove a company's logo (without deleting the company)",
    response_model=ApiResponse[WorkResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Work not found or has no logo"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Work"],
)
def api_admin_delete_work_logo(
    work_id: str,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[WorkResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_delete_work_logo(work_id, db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=WorkResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_delete_work_logo",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
