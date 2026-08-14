from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_WORK_ITEM_UPDATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.work.items.update import WorkItemUpdatePayload
from api.schemas.work.response import WorkItemResponseData
from api.status import STATUS_BY_KEY
from core.handler.work.items.update import handler_update_work_item
from database.psql.database import get_db

router = APIRouter()


@router.put(
    ADMIN_WORK_ITEM_UPDATE,
    summary="[Admin] Update a work item",
    response_model=ApiResponse[WorkItemResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Work"],
)
def api_admin_update_work_item(
    work_id: str,
    item_id: str,
    body: WorkItemUpdatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[WorkItemResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_update_work_item(
            work_id, item_id, db_session=db, **body.model_dump(exclude_unset=True)
        )
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=WorkItemResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_update_work_item",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
