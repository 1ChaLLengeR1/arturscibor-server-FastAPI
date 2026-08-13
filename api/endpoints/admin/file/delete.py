from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_FILE_DELETE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.file.delete import DeleteFileResponseData
from core.handler.file.delete import handler_delete_file
from database.psql.database import get_db

router = APIRouter()

_STATUS_BY_KEY = {"NotFound": 404}


@router.delete(
    ADMIN_FILE_DELETE,
    summary="[Admin] Usuń plik",
    response_model=ApiResponse[DeleteFileResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Plik nie znaleziony"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/File"],
)
def api_admin_delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[DeleteFileResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_delete_file(file_id=file_id, db_session=db)
        if not ok:
            status_code = _STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=DeleteFileResponseData(deleted=result.deleted, id=result.id))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_delete_file", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
