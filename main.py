from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.exception_handlers import register_exception_handlers
from api.router import api_router

# Old, not-yet-migrated domains (routers/) are unplugged on purpose — see
# docs/3.2-3.5-*.md. Files still exist on disk, just not imported/included
# here, so only the migrated endpoints (currently: auth) are live.

app = FastAPI()

register_exception_handlers(app)

app.mount("/file", StaticFiles(directory="file"), name="file")

origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
