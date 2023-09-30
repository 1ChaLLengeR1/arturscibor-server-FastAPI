from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers.authentication import auth
from routers.Home import jobs, information_cv, images_me
from routers.AboutMe import informationme, readmore
from routers.Tools import tools
from routers.Projects import project, technologies, images, download_project
from routers.Contact import contact

app = FastAPI()

app.mount("/file", StaticFiles(directory="file"), name="file")

origins = [
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
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

