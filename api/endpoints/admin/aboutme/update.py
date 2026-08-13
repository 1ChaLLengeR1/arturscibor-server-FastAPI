from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_ABOUT_ME_UPDATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.aboutme.response import AboutMeResponseData
from api.schemas.aboutme.update import AboutMeUpdatePayload
from core.handler.aboutme.update import handler_update_about_me
from database.psql.database import get_db

router = APIRouter()

_STATUS_BY_KEY = {"NotFound": 404}


@router.put(
    ADMIN_ABOUT_ME_UPDATE,
    summary="[Admin] Update about me",
    response_model=ApiResponse[AboutMeResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/AboutMe"],
)
def api_admin_update_about_me(
    body: AboutMeUpdatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[AboutMeResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_update_about_me(db_session=db, **body.model_dump(exclude_unset=True))
        if not ok:
            status_code = _STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=AboutMeResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_update_about_me",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
