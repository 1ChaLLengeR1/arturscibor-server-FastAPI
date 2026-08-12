from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_CONTACT_COLLECTION
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.contact.response import ContactResponseData
from core.handler.contact.collection import handler_collection_contact
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
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[list[ContactResponseData], None] | JSONResponse:
    try:
        result, error, ok = handler_collection_contact(db_session=db)
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
