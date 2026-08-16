from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import PROJECTS_ONE
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from api.schemas.projects.response import ProjectResponseData
from api.status import STATUS_BY_KEY
from core.handler.projects.one import handler_one_project
from database.psql.database import get_db

router = APIRouter()


@router.get(
    PROJECTS_ONE,
    summary="[Public] Get a single project",
    response_model=ApiResponse[ProjectResponseData, None],
    responses={
        404: {"model": ApiErrorResponse, "description": "Not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Projects"],
)
def api_one_project(
    project_id: str,
    lang: str = Query(default=DEFAULT_LANGUAGE_CODE),
    db: Session = Depends(get_db),
) -> ApiResponse[ProjectResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_one_project(project_id, lang=lang, db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=ProjectResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_one_project", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
