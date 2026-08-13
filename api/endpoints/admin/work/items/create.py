from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_WORK_ITEM_CREATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.work.items.create import WorkItemCreatePayload
from api.schemas.work.response import WorkItemResponseData
from core.handler.work.items.create import handler_create_work_item
from database.psql.database import get_db

router = APIRouter()

_STATUS_BY_KEY = {"NotFound": 404}


@router.post(
    ADMIN_WORK_ITEM_CREATE,
    summary="[Admin] Add a work item (position) under a company",
    response_model=ApiResponse[WorkItemResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Work not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=201,
    tags=["Admin/Work"],
)
def api_admin_create_work_item(
    work_id: str,
    body: WorkItemCreatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[WorkItemResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_create_work_item(
            work_id,
            body.title.model_dump(),
            body.employment_type,
            body.location.model_dump() if body.location else None,
            body.date_from,
            body.date_to,
            body.body_markdown.model_dump() if body.body_markdown else None,
            body.skills,
            db_session=db,
        )
        if not ok:
            status_code = _STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=201, data=WorkItemResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_create_work_item",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
