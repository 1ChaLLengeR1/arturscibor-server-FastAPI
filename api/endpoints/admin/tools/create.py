from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_TOOLS_CREATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.tools.create import ToolCreatePayload
from api.schemas.tools.response import ToolResponseData
from core.handler.tools.create import handler_create_tool
from database.psql.database import get_db

router = APIRouter()


@router.post(
    ADMIN_TOOLS_CREATE,
    summary="[Admin] Create a tool",
    response_model=ApiResponse[ToolResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=201,
    tags=["Admin/Tools"],
)
def api_admin_create_tool(
    body: ToolCreatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[ToolResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_create_tool(
            body.name.model_dump(),
            body.information.model_dump() if body.information else None,
            body.progress,
            body.numeric,
            body.link,
            db_session=db,
        )
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=201, data=ToolResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_create_tool", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
