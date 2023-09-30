import random
from fastapi import APIRouter, Depends, status, UploadFile, Form
from typing import List
from DataBase.db import SessionLocal
from JWT.authenticationRouter import check_bearer_token
from fastapi.responses import JSONResponse
from DataBase.models import ImagesProjects
from decouple import config
from routers.Projects.schemas import ImageId
import os

router = APIRouter()
db = SessionLocal()


@router.post('/projects/images/add_images')
async def add_images(id_project: str = Form(), images: List[UploadFile] = None, type: str = Form()):
    try:
        numer_random = random.random()
        for image in images:
            if image.filename == 'brak.txt' or image.size == 0 or image is None:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak zdjęć!"})
            else:
                new_item = ImagesProjects(id_project=id_project, name=image.filename,
                                          path=f"./file/imagesproject/{type}-{id_project}-{numer_random}-{image.filename}",
                                          link=f"{config('SERVER')}/file/imagesproject/{type}-{id_project}-{numer_random}-{image.filename}",
                                          type=type)

                file_path = f"./file/imagesproject/{type}-{id_project}-{numer_random}-{image.filename}"
                with open(file_path, "wb") as f:
                    context = await image.read()
                    f.write(context)

                db.add(new_item)

        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Dodano poprawnie zdjęcia!"})

    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": ""})


@router.delete('/projects/images/delete_image')
async def delete_image(payload: ImageId):
    try:
        item_delete_id = db.query(ImagesProjects).filter(ImagesProjects.id == payload.id)
        item_delete = item_delete_id.first()

        if not item_delete:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak id zdjęcia!"})

        if os.path.exists(item_delete.path):
            os.remove(item_delete.path)

        item_delete_id.delete(synchronize_session=False)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie usunięto zdjęcie!"})

    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas usuwania zdjęcia!"})
