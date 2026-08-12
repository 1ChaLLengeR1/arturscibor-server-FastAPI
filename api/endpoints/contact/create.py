from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import CONTACT_CREATE
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.contact.create import ContactCreatePayload
from api.schemas.contact.response import ContactResponseData
from core.handler.contact.create import handler_create_contact
from database.psql.database import get_db

router = APIRouter()


@router.post(
    CONTACT_CREATE,
    summary="[Guest] Send a contact message",
    response_model=ApiResponse[ContactResponseData, None],
    responses={500: {"model": ApiErrorResponse, "description": "Unexpected server error"}},
    status_code=201,
    tags=["Contact"],
)
def api_create_contact(
    body: ContactCreatePayload, db: Session = Depends(get_db)
) -> ApiResponse[ContactResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_create_contact(
            body.name, body.email, body.subject, body.phone, body.description, db_session=db
        )
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=201, data=ContactResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_create_contact", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
