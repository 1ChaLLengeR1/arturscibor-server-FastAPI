from fastapi import Depends, status, APIRouter, Form, File, UploadFile
import os
from typing import List
from routers.Home.schemas import HomeDeleteImageMe
from JWT.authenticationRouter import check_bearer_token
from fastapi.responses import JSONResponse
from DataBase.models import ImagesMe
from DataBase.db import SessionLocal
from decouple import config

router = APIRouter()
db = SessionLocal()


@router.get('/home/images_me/get_images')
async def get_images():
    try:
        images = db.query(ImagesMe).all()
        return images

    except():
        return JSONResponse(status_code=status.HTTP_HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas pobierania zdjęć!"})


@router.post('/home/images_me/add_images', dependencies=[Depends(check_bearer_token)])
async def add_images(images: List[UploadFile] = File(None)):
    try:

        if images[0].size == 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"error": "Brak jakikolwiek zdjęć do dodania!"})

        for image in images:
            new_item = ImagesMe(name=image.filename, path=f"./file/portfolioImage/{image.filename}", link=f"{config('SERVER')}/file/portfolioImage/{image.filename}")
            db.add(new_item)
            db.commit()

            file_path = f"./file/portfolioImage/{image.filename}"
            with open(file_path, "wb") as f:
                content = await image.read()
                f.write(content)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Dodano poprawnie zdjęcia do Portfolio!"})
    except():
        return JSONResponse(status_code=status.HTTP_HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas dodawnia do zdjęć do Portfolio!"})


@router.delete('/home/images_me/delete_image', dependencies=[Depends(check_bearer_token)])
async def delete_image(payload: HomeDeleteImageMe | None = None):
    try:

        item_id = db.query(ImagesMe).filter(ImagesMe.id == payload.id)
        item = item_id.first()

        if not item:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak takiego id!"})

        file_path = f"./file/portfolioImage/{item.name}"
        if os.path.exists(file_path):
            os.remove(file_path)

        item_id.delete(synchronize_session=False)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Usunięto poprawnie zdjęcie!"})



    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas usuwania zdjęcia!"})
