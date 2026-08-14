from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_FILE_CONFIRM
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.file.response import FileItemData
from api.status import STATUS_BY_KEY
from core.handler.file.confirm import handler_confirm_file
from database.psql.database import get_db

router = APIRouter()


@router.patch(
    ADMIN_FILE_CONFIRM,
    summary="[Admin] Potwierdź upload pliku",
    response_model=ApiResponse[FileItemData, None],
    responses={
        400: {"model": ApiErrorResponse, "description": "Zły status lub brak pliku na dysku"},
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Plik nie znaleziony"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/File"],
)
def api_admin_confirm_file(
    file_id: str,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[FileItemData, None] | JSONResponse:
    try:
        result, error, ok = handler_confirm_file(file_id=file_id, db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=FileItemData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_confirm_file", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
