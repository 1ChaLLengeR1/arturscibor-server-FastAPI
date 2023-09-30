import random
from fastapi import Depends, status, APIRouter, Form, UploadFile
import os
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import FileProjects
from decouple import config
from routers.Projects.schemas import DwonloadProjectPath

router = APIRouter()
db = SessionLocal()


@router.post('/projects/download_project/download_project')
async def download_project(payload: DwonloadProjectPath):
    try:

        directory = './file/downloadFilesProject/'
        item_download_project = payload.path

        file_path = None

        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if f == item_download_project:
                if os.path.isfile(f):
                    file_path = f

        return FileResponse(path=file_path, filename=file_path, media_type="application/rar")


    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas pobierania projektu RAR!"})


@router.put('/projects/download_project/update_file_project')
async def update_file_project(id: str = Form(), id_project: str = Form(), file: UploadFile | None = None):
    try:
        item_update_id = db.query(FileProjects).filter(FileProjects.id == id)
        item_update = item_update_id.first()

        if os.path.exists(item_update.path):
            os.remove(item_update.path)

        random_number = random.random()
        path_file_download_project = f'./file/downloadFilesProject/{random_number}-{id_project}-{file.filename}'
        with open(path_file_download_project, 'wb') as f:
            context = await file.read()
            f.write(context)

        item_update.path = path_file_download_project
        item_update.link = f"{config('SERVER')}/file/downloadFilesProject/{random_number}-{id_project}-{file.filename}"
        item_update.name = file.filename

        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie z modyfikowano plik!"})

    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas modyfikacji projektu!"})
