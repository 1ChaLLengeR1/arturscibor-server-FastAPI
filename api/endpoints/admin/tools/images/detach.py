from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_TOOLS_IMAGE_DETACH
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.tools.response import ToolResponseData
from core.handler.tools.images.detach import handler_detach_tool_image
from database.psql.database import get_db

router = APIRouter()

_STATUS_BY_KEY = {"NotFound": 404}


@router.delete(
    ADMIN_TOOLS_IMAGE_DETACH,
    summary="[Admin] Detach and delete a file from a tool",
    response_model=ApiResponse[ToolResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Tool, file, or attachment not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Tools"],
)
def api_admin_detach_tool_image(
    tool_id: str,
    file_id: str,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[ToolResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_detach_tool_image(tool_id, file_id, db_session=db)
        if not ok:
            status_code = _STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=ToolResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_detach_tool_image",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
