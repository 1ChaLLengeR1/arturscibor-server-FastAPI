from fastapi import APIRouter, Depends, status, Form, UploadFile
from typing import List
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import Contact, ImagesMessage
from routers.Contact.schemas import DeleteMessage, GetIdMessage
import os
import uuid
import random
from decouple import config

router = APIRouter()
db = SessionLocal()


@router.post('/contact/contact/add_message')
async def add_message(name: str = Form(), email: str = Form(), description: str = Form(),
                      files: List[UploadFile] = None):
    try:
        uuid_v4 = uuid.uuid4()
        new_message = Contact(id=uuid_v4, name=name, email=email, description=description)
        random_random = random.random()
        for image in files:
            if image.filename == 'brak.txt' or image.size == 0 or image is None:
                pass
            else:
                new_image = ImagesMessage(id_message=uuid_v4,
                                          path=f"./file/imagesmessage/{random_random}-{image.filename}",
                                          link=f"{config('SERVER')}/file/imagesmessage/{random_random}-{image.filename}")

                file_path = f"./file/imagesmessage/{random_random}-{image.filename}"
                with open(file_path, 'wb') as f:
                    context = await image.read()
                    f.write(context)

                db.add(new_image)

        db.add(new_message)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Wysłano poprawnie wiadomość!"})


    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas dodawania wiadomości!"})


@router.delete('/contact/contact/delete_message', dependencies=[Depends(check_bearer_token)])
async def delete_message(payload: DeleteMessage):
    try:
        item_contact_id = db.query(Contact).filter(Contact.id == payload.id)
        item_contact = item_contact_id.first()

        if not item_contact:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak id wiadomości!"})
        item_contact_id.delete(synchronize_session=False)

        item_images_id = db.query(ImagesMessage).filter(ImagesMessage.id_message == payload.id)
        item_images = item_images_id.all()
        for image in item_images:
            if os.path.exists(image.path):
                os.remove(image.path)

        item_images_id.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie usunięto wiadomość"})

    except(FileNotFoundError, Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas usuwania wiadomości!"})


@router.get('/contact/contact/get_messages')
async def get_projects():
    try:
        items_message = db.query(Contact).all()
        array_object = []
        for items in items_message:
            item = {
                "id": items.id,
                "name": items.name,
            }
            array_object.append(item)

        return array_object

    except(Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas pobierania wiadomości!"})


@router.post('/contact/contact/get_message', dependencies=[Depends(check_bearer_token)])
async def get_message(payload: GetIdMessage):
    try:
        item_message_id = db.query(Contact).filter(Contact.id == payload.id)
        item_message = item_message_id.first()

        if not item_message:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Brak id wiadomości!"})

        item_message_images_id = db.query(ImagesMessage).filter(ImagesMessage.id_message == payload.id)
        item_message_images = item_message_images_id.all()

        item_object_message = {
            "id": item_message.id,
            "name": item_message.name,
            "email": item_message.email,
            "description": item_message.description,
            "images_message": item_message_images
        }

        return item_object_message

    except(Exception, FileNotFoundError):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={'error': "Błąd podczas pobierania wiadomości!"})
