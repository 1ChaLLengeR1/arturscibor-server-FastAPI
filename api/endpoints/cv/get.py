from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import CV
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.cv.response import CurriculumVitaeResponseData
from core.handler.cv.get import handler_get_cv
from database.psql.database import get_db

router = APIRouter()


@router.get(
    CV,
    summary="[Public] Get current CV metadata",
    response_model=ApiResponse[CurriculumVitaeResponseData, None],
    responses={
        404: {"model": ApiErrorResponse, "description": "Not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["CV"],
)
def api_get_cv(db: Session = Depends(get_db)) -> ApiResponse[CurriculumVitaeResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_get_cv(db_session=db)
        if not ok:
            status_code = 404 if error.key_type_error == "NotFound" else 400
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=CurriculumVitaeResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_get_cv", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
