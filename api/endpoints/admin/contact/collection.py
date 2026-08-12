from dataclasses import asdict
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_CONTACT_COLLECTION
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.contact.response import ContactResponseData
from core.handler.contact.collection import handler_collection_contact
from core.repository.psql.contact.collection import DEFAULT_LIMIT
from database.psql.database import get_db

router = APIRouter()


@router.get(
    ADMIN_CONTACT_COLLECTION,
    summary="[Admin] List contact messages",
    response_model=ApiResponse[list[ContactResponseData], None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Contact"],
)
def api_admin_collection_contact(
    limit: int = Query(default=DEFAULT_LIMIT, gt=0, le=100),
    is_read: bool | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[list[ContactResponseData], None] | JSONResponse:
    try:
        result, error, ok = handler_collection_contact(
            limit=limit,
            is_read=is_read,
            created_from=created_from,
            created_to=created_to,
            db_session=db,
        )
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=200, data=[ContactResponseData(**asdict(item)) for item in result])
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_collection_contact",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
