from fastapi import Depends, status, APIRouter, Form, UploadFile
import os
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import CurriculumVitae, Information
from routers.Home.schemas import InformationMe
from decouple import config

router = APIRouter()
db = SessionLocal()


@router.get('/home/information-cv/download-cv')
async def download_cv():
    try:
        directory = './file/cv/'
        file_path = None

        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                file_path = f

        return FileResponse(path=file_path, filename=file_path, media_type="application/pdf")
    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas pobierania CV"})


@router.get('/home/information-cv/cv')
async def get_cv():
    try:
        items_cv = db.query(CurriculumVitae).all()
        return items_cv
    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas pobierania CV"})


@router.put('/home/information-cv/upload-cv', dependencies=[Depends(check_bearer_token)])
async def upload_cv(id_cv: str = Form(...), cv: UploadFile | None = None):
    try:

        print(cv.filename)
        if cv.size == 0 or cv.filename == 'brak.txt':
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"error": "Brak pliku do zmiany CV"})

        item_id = db.query(CurriculumVitae).filter(CurriculumVitae.id == id_cv)
        item_cv = item_id.first()

        if not item_cv:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"error": "Brak takiego id!"})

        if os.path.exists(item_cv.path):
            os.remove(item_cv.path)
        file_name = f"arturscibor_cv-{cv.filename}"
        file_path = f"./file/cv/{file_name}"
        with open(file_path, "wb") as f:
            content = await cv.read()
            f.write(content)

        item_cv.name = file_name
        item_cv.path = file_path
        item_cv.link = f"{config('SERVER')}/file/cv/{file_name}"
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Pomyślnie zmieniono CV!"})
    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas zmiany CV"})


@router.put('/home/information-cv/upload-me', dependencies=[Depends(check_bearer_token)])
async def upload_information_me(payload: InformationMe | None = None):
    try:
        id = db.query(Information).filter(Information.id == payload.id)
        item = id.first()

        if not item:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"error": "Brak takiego Id!"})
        item.information = payload.information
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Poprawnie z edytowano InformationMe!"})

    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas edytowania InformationMe!"})


@router.get('/home/information-cv/information-me')
async def get_information_me():
    try:
        item = db.query(Information).all()
        return item
    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas pobierania InformationMe"})
