from fastapi import Depends, status, APIRouter, Form, UploadFile
import os
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import AboutMe
from decouple import config

router = APIRouter()
db = SessionLocal()


@router.get('/aboutme/information/get-me')
async def get_me():
    try:
        item = db.query(AboutMe).all()
        return item
    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error":"Błąd podczas poberania AboutMe!"})

@router.put('/aboutme/information/upload-me', dependencies=[Depends(check_bearer_token)])
async def upload_me(item_id: str = Form(...), name: str = Form(...), job: str = Form(...), information: str = Form(...),
                    file: UploadFile | None = None):
    try:

        item = db.query(AboutMe).filter(AboutMe.id == item_id)
        item_me = item.first()

        if not item_me:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"error": "Brak takiego id!"})

        item_me.name = name
        item_me.job = job
        item_me.information = information

        file_path = f"./file/aboutmeImage/{file.filename}"
        if file.size == 0 or file.filename == 'brak.txt':
            pass
        else:
            if os.path.exists(item_me.path_image):
                os.remove(item_me.path_image)

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            item_me.path_image = file_path
            item_me.link_image = f"{config('SERVER')}/file/aboutmeImage/{file.filename}"

        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Poprawnie zedytowano AboutMe!"})
    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas edytowania AboutMe!"})
