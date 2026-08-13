from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_FILE_INIT
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.file.init import FileInitPayload, FileInitResponseData
from core.handler.file.init import handler_init_file
from database.psql.database import get_db

router = APIRouter()


@router.post(
    ADMIN_FILE_INIT,
    summary="[Admin] Inicjuj upload pliku",
    response_model=ApiResponse[FileInitResponseData, None],
    responses={
        400: {"model": ApiErrorResponse, "description": "Niedozwolony katalog lub rozszerzenie"},
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=201,
    tags=["Admin/File"],
)
def api_admin_init_file(
    body: FileInitPayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[FileInitResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_init_file(
            original_name=body.original_name,
            size=body.size,
            directory=body.directory,
            file_type=body.file_type,
            mime_type=body.mime_type,
            db_session=db,
        )
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=201, data=FileInitResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_init_file", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
