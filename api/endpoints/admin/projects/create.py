from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_PROJECTS_CREATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.projects.create import ProjectCreatePayload
from api.schemas.projects.response import ProjectResponseData
from core.handler.projects.create import handler_create_project
from database.psql.database import get_db

router = APIRouter()


@router.post(
    ADMIN_PROJECTS_CREATE,
    summary="[Admin] Create a project",
    response_model=ApiResponse[ProjectResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=201,
    tags=["Admin/Projects"],
)
def api_admin_create_project(
    body: ProjectCreatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[ProjectResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_create_project(
            body.name,
            body.short_description.model_dump() if body.short_description else None,
            body.description.model_dump() if body.description else None,
            body.level,
            body.technologies,
            body.github_url,
            body.live_url,
            body.completed_at,
            body.started_at,
            body.is_support,
            body.numeric,
            db_session=db,
        )
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=201, data=ProjectResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_create_project",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
