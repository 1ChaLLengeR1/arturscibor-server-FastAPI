from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ABOUT_ME
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.aboutme.response import AboutMeResponseData
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from api.status import STATUS_BY_KEY
from core.handler.aboutme.get import handler_get_about_me
from database.psql.database import get_db

router = APIRouter()


@router.get(
    ABOUT_ME,
    summary="[Public] Get about me",
    response_model=ApiResponse[AboutMeResponseData, None],
    responses={
        404: {"model": ApiErrorResponse, "description": "Not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["AboutMe"],
)
def api_get_about_me(
    lang: str = Query(default=DEFAULT_LANGUAGE_CODE),
    db: Session = Depends(get_db),
) -> ApiResponse[AboutMeResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_get_about_me(lang=lang, db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=AboutMeResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_get_about_me", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
