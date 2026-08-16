from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_PROJECTS_IMAGE_DETACH
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.projects.response import ProjectResponseData
from api.status import STATUS_BY_KEY
from core.handler.projects.images.detach import handler_detach_project_image
from database.psql.database import get_db

router = APIRouter()


@router.delete(
    ADMIN_PROJECTS_IMAGE_DETACH,
    summary="[Admin] Detach and delete a file from a project",
    response_model=ApiResponse[ProjectResponseData, None],
    responses={
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Project, file, or attachment not found"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Projects"],
)
def api_admin_detach_project_image(
    project_id: str,
    file_id: str,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[ProjectResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_detach_project_image(project_id, file_id, db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=ProjectResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_detach_project_image",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
