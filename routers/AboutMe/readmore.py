from fastapi import Depends, status, APIRouter
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from DataBase.db import SessionLocal
from DataBase.models import ReadMore
from routers.AboutMe.schemas import ReadMoreAddItem, ReadMoreUpdateItem, ReadMoreId

router = APIRouter()
db = SessionLocal()


@router.get('/aboutme/readmore/get_items')
async def get_items():
    try:
        items = db.query(ReadMore).all()
        return items
    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas poberania readMore!"})


@router.post('/aboutme/readmore/add_item', dependencies=[Depends(check_bearer_token)])
async def add_item(item: ReadMoreAddItem):
    try:
        new_item = ReadMore(name=item.name, information=item.information, numeric=item.numeric)
        db.add(new_item)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie dodano do ReadMore!"})
    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Błąd podczas dodawania!"})


@router.put('/aboutme/readmore/update_item', dependencies=[Depends(check_bearer_token)])
async def update_item(item: ReadMoreUpdateItem):
    try:
        item_id = db.query(ReadMore).filter(ReadMore.id == item.id)
        item_update = item_id.first()

        if not item_update:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"error": "Brak takiego id!"})

        item_update.name = item.name
        item_update.information = item.information
        item_update.numeric = item.numeric
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie zedytowano ReadMoreItem"})
    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas edytowania ReadMoreItem!"})

@router.delete('/aboutme/readmore/delete_item', dependencies=[Depends(check_bearer_token)])
async def delete_item(item: ReadMoreId):
    try:
        item_id = db.query(ReadMore).filter(ReadMore.id == item.id)
        item_delete = item_id.first()

        if not item_delete:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"error": "Brak takiego id!"})

        item_id.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie usunięto ReadMoreItem!"})
    except():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas usuwania ReadMoreItem!"})