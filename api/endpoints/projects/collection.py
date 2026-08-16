from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import PROJECTS_COLLECTION
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from api.schemas.projects.response import ProjectResponseData
from core.handler.projects.collection import handler_collection_projects
from database.psql.database import get_db

router = APIRouter()


@router.get(
    PROJECTS_COLLECTION,
    summary="[Public] List projects",
    response_model=ApiResponse[list[ProjectResponseData], None],
    responses={500: {"model": ApiErrorResponse, "description": "Unexpected server error"}},
    status_code=200,
    tags=["Projects"],
)
def api_collection_projects(
    lang: str = Query(default=DEFAULT_LANGUAGE_CODE),
    db: Session = Depends(get_db),
) -> ApiResponse[list[ProjectResponseData], None] | JSONResponse:
    try:
        result, error, ok = handler_collection_projects(lang=lang, db_session=db)
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=200, data=[ProjectResponseData(**asdict(item)) for item in result])
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_collection_projects",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
