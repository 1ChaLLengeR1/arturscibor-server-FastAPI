from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.exception_handlers import register_exception_handlers
from api.router import api_router
from routers.AboutMe import informationme, readmore
from routers.Contact import contact

# Old, not-yet-migrated domains — see docs/3.2-3.5-*.md
from routers.Home import images_me, information_cv, jobs
from routers.Projects import download_project, images, project, technologies
from routers.Tools import tools

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

app.include_router(jobs.router)
app.include_router(information_cv.router)
app.include_router(images_me.router)
app.include_router(informationme.router)
app.include_router(readmore.router)
app.include_router(tools.router)
app.include_router(project.router)
app.include_router(technologies.router)
app.include_router(images.router)
app.include_router(download_project.router)
app.include_router(contact.router)
