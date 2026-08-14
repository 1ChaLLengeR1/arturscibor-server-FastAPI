from dataclasses import asdict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_FILE_UPLOAD
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.file.response import FileItemData
from api.status import STATUS_BY_KEY
from core.handler.file.upload import handler_upload_file
from database.psql.database import get_db

router = APIRouter()


@router.put(
    ADMIN_FILE_UPLOAD,
    summary="[Admin] Wgraj plik (raw bytes)",
    response_model=ApiResponse[FileItemData, None],
    responses={
        400: {"model": ApiErrorResponse, "description": "Niezgodny MIME, rozmiar lub nieprawidłowy status"},
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Plik nie znaleziony"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/File"],
    openapi_extra={
        "requestBody": {
            "content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}},
            "required": True,
        }
    },
)
async def api_admin_upload_file(
    request: Request,
    file_id: str,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[FileItemData, None] | JSONResponse:
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "")

        result, error, ok = handler_upload_file(
            file_id=file_id,
            body=body,
            content_type=content_type,
            db_session=db,
        )
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=FileItemData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_upload_file", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
