from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_CV_UPLOAD
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.cv.response import CurriculumVitaeResponseData
from api.schemas.cv.upload import CvUploadPayload
from core.handler.cv.upload import handler_upload_cv
from database.psql.database import get_db

router = APIRouter()

_STATUS_BY_KEY = {"NotFound": 404}


@router.put(
    ADMIN_CV_UPLOAD,
    summary="[Admin] Replace the current CV",
    response_model=ApiResponse[CurriculumVitaeResponseData, None],
    responses={
        400: {"model": ApiErrorResponse, "description": "File is not a confirmed document"},
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "CV or file not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/CV"],
)
def api_admin_upload_cv(
    body: CvUploadPayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[CurriculumVitaeResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_upload_cv(body.file_id, db_session=db)
        if not ok:
            status_code = _STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=CurriculumVitaeResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_admin_upload_cv", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
