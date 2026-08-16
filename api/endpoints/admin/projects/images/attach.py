from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import ADMIN_PROJECTS_IMAGE_ATTACH
from api.middleware.Authentication import JWTAuthenticationMiddleware
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.projects.image import ProjectImageAttachPayload
from api.schemas.projects.response import ProjectResponseData
from api.status import STATUS_BY_KEY
from core.handler.projects.images.attach import handler_attach_project_image
from database.psql.database import get_db

router = APIRouter()


@router.post(
    ADMIN_PROJECTS_IMAGE_ATTACH,
    summary="[Admin] Attach a confirmed file to a project",
    response_model=ApiResponse[ProjectResponseData, None],
    responses={
        400: {"model": ApiErrorResponse, "description": "File is not confirmed"},
        403: {"model": ApiErrorResponse, "description": "Forbidden"},
        404: {"model": ApiErrorResponse, "description": "Project or file not found"},
        409: {"model": ApiErrorResponse, "description": "File already attached to a project"},
        500: {"model": ApiErrorResponse, "description": "Unexpected server error"},
    },
    status_code=200,
    tags=["Admin/Projects"],
)
def api_admin_attach_project_image(
    project_id: str,
    body: ProjectImageAttachPayload,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"])),
) -> ApiResponse[ProjectResponseData, None] | JSONResponse:
    try:
        result, error, ok = handler_attach_project_image(project_id, body.file_id, db_session=db)
        if not ok:
            status_code = STATUS_BY_KEY.get(error.key_type_error, 400)
            return JSONResponse(
                status_code=status_code, content=ApiErrorResponse(status_code=status_code, data=error).model_dump()
            )
        return ApiResponse(status_code=200, data=ProjectResponseData(**asdict(result)))
    except Exception as e:
        error = ApiErrorData(
            message=str(e),
            type_module="api_admin_attach_project_image",
            type_error="exception",
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
