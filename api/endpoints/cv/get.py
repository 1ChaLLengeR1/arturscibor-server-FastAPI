from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import CV
from api.response import ApiErrorData, ApiErrorResponse
from api.status import STATUS_BY_KEY
from core.handler.cv.get import handler_get_cv
from database.psql.database import get_db

router = APIRouter()


@router.get(
    CV,
    summary="[Public] Download the current CV file",
    response_model=None,
    responses={
        404: {"model": ApiErrorResponse, "description": "CV not set or missing on disk"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["CV"],
)
def api_get_cv(db: Session = Depends(get_db)) -> FileResponse | JSONResponse:
    try:
        result, error, ok = handler_get_cv(db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return FileResponse(path=result.path, filename=result.filename, media_type=result.media_type)
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_get_cv", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
