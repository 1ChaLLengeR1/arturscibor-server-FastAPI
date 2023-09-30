from fastapi import Depends, status, APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import Tools
from routers.Tools.schemas import ItemDeleteTools
import os
import random
from decouple import config

router = APIRouter()
db = SessionLocal()


@router.get("/tools/tools/get_items")
async def get_items():
    try:
        items = db.query(Tools).all()
        return items

    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas pobierania tools!"})


@router.put("/tools/tools/upload_item", dependencies=[Depends(check_bearer_token)])
async def upload_item(id: str = Form(), name: str = Form(), information: str = Form(), progress: str = Form(),
                      numeric: int = Form(),
                      link: str = Form(), file: UploadFile = File(None)):
    try:
        item_id = db.query(Tools).filter(Tools.id == id)
        item = item_id.first()

        if not item:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak takiego id!"})

        item.name = name
        item.information = information
        item.progress = progress
        item.numeric = numeric
        item.link = link

        if file.size == 0 or file.filename == 'brak.txt' or file is None:
            pass
        else:
            if os.path.exists(item.path_image):
                os.remove(item.path_image)

            random_numer_path = random.random()
            file_path = f"./file/tools/{file.size}-{random_numer_path}-{file.filename}"

            with open(file_path, "wb") as f:
                context = await file.read()
                f.write(context)

            item.path_image = file_path
            item.link_image = f"{config('SERVER')}/file/tools/{file.size}-{random_numer_path}-{file.filename}"

        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie zaktualizowano Tools!"})


    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Błąd przy upload tools"})


@router.post("/tools/tools/add_item", dependencies=[Depends(check_bearer_token)])
async def add_item(name: str = Form(), information: str = Form(), progress: str = Form(), numeric: int = Form(),
                   link: str = Form(), file: UploadFile = File(None)):
    try:
        if file.size == 0 or file.filename == 'brak.txt':
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak zdjęcia/svg!"})
        else:
            path_random = random.random()
            new_item = Tools(name=name, information=information, progress=progress, numeric=numeric, link=link,
                             path_image=f"./file/tools/{file.size}-{path_random}-{file.filename}",
                             link_image=f"{config('SERVER')}/file/tools/{file.size}-{path_random}-{file.filename}")

            db.add(new_item)
            db.commit()

            file_path = f"./file/tools/{file.size}-{path_random}-{file.filename}"
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Dodano poprawnie Tools!"})

    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Błąd przy dodawaniu tools"})


@router.delete("/tools/tools/delete_item", dependencies=[Depends(check_bearer_token)])
async def delete_item(payload: ItemDeleteTools):
    try:
        item_id = db.query(Tools).filter(Tools.id == payload.id)
        item = item_id.first()

        if not item:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak takiego id!"})

        if os.path.exists(item.path_image):
            os.remove(item.path_image)

        item_id.delete(synchronize_session=False)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Usunięto poprawnie item Tools!"})

    except():
        return JSONResponse(status_code=status.HTTP_200_OK, content={"error": "Błąd podczas usuwania Tools!"})
