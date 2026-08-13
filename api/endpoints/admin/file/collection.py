from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_FILE_COLLECTION
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.file.collection import FileCollectionResponseData
from api.schemas.file.response import FileItemData, PaginationData
from core.handler.file.collection import handler_collection_files
from core.repository.psql.file.collection import DEFAULT_LIMIT
from database.psql.database import get_db
from database.psql.models.file import FileStatus, FileType

router = APIRouter()


@router.get(
    ADMIN_FILE_COLLECTION,
    summary="[Admin] Lista plików",
    response_model=ApiResponse[FileCollectionResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/File"],
)
def api_admin_collection_files(
    directory: str | None = Query(default=None),
    file_type: FileType | None = Query(default=None),
    status: FileStatus | None = Query(default=None),
    original_name: str | None = Query(default=None),
    limit: int = Query(default=DEFAULT_LIMIT, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[FileCollectionResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_collection_files(
            directory=directory,
            file_type=file_type,
            status=status,
            original_name=original_name,
            limit=limit,
            offset=offset,
            db_session=db,
        )
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(
            status_code=200,
            data=FileCollectionResponseData(
                items=[FileItemData(**asdict(item)) for item in result.items],
                pagination=PaginationData(
                    total=result.total,
                    has_more=(offset + limit) < result.total,
                    limit=limit,
                    offset=offset,
                ),
            ),
        )
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_collection_files",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
