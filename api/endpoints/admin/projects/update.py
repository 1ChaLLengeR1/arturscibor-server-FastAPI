from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_PROJECTS_UPDATE
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.projects.response import ProjectResponseData
from api.schemas.projects.update import ProjectUpdatePayload
from api.status import STATUS_BY_KEY
from core.handler.projects.update import handler_update_project
from database.psql.database import get_db

router = APIRouter()


@router.put(
    ADMIN_PROJECTS_UPDATE,
    summary="[Admin] Update a project",
    response_model=ApiResponse[ProjectResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Projects"],
)
def api_admin_update_project(
    project_id: str,
    body: ProjectUpdatePayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[ProjectResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_update_project(project_id, db_session=db, **body.model_dump(exclude_unset=True))
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=ProjectResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_update_project",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
