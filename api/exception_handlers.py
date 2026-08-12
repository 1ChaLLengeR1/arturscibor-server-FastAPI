import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.response import ApiErrorData, ApiErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s", request.url.path)
        error = ApiErrorData(
            message="Unexpected server error",
            type_module=request.url.path,
            type_error=type(exc).__name__,
            key_type_error="Exception",
        )
        return JSONResponse(status_code=500, content=ApiErrorResponse(status_code=500, data=error).model_dump())
