from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.endpoints.urls import TOOLS_COLLECTION
from api.response import ApiErrorData, ApiErrorResponse, ApiResponse
from api.schemas.common.multi_lang import DEFAULT_LANGUAGE_CODE
from api.schemas.tools.response import ToolResponseData
from core.handler.tools.collection import handler_collection_tools
from database.psql.database import get_db

router = APIRouter()


@router.get(
    TOOLS_COLLECTION,
    summary="[Public] List tools",
    response_model=ApiResponse[list[ToolResponseData], None],
    responses={500: {"model": ApiErrorResponse, "description": "Unexpected server error"}},
    status_code=200,
    tags=["Tools"],
)
def api_collection_tools(
    lang: str = Query(default=DEFAULT_LANGUAGE_CODE),
    db: Session = Depends(get_db),
) -> ApiResponse[list[ToolResponseData], None] | JSONResponse:
    try:
        result, error, ok = handler_collection_tools(lang=lang, db_session=db)
        if not ok:
            return JSONResponse(status_code=400, content=ApiErrorResponse(status_code=400, data=error).model_dump())
        return ApiResponse(status_code=200, data=[ToolResponseData(**asdict(item)) for item in result])
    except Exception as e:
        error = ApiErrorData(
            message=str(e), type_module="api_collection_tools", type_error="exception", key_type_error="Exception"
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
