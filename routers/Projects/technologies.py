from fastapi import APIRouter, Depends, status
from DataBase.db import SessionLocal
from JWT.authenticationRouter import check_bearer_token
from fastapi.responses import JSONResponse
from DataBase.models import TechnologiesProject
from routers.Projects.schemas import AddTechnologyItem, DeleteTechnologyId

router = APIRouter()
db = SessionLocal()


@router.post('/projects/technologies/add_technology', dependencies=[Depends(check_bearer_token)])
async def add_technology(payload: AddTechnologyItem):
    try:
        new_item = TechnologiesProject(id_project=payload.id_project, name=payload.name)
        db.add(new_item)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Dodano poprawnie technologie!"})
    except(Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas dodawania technologii!"})


@router.delete('/projects/technologies/delete_technology', dependencies=[Depends(check_bearer_token)])
async def delete_technology(payload: DeleteTechnologyId):
    try:
        delete_item_id = db.query(TechnologiesProject).filter(TechnologiesProject.id == payload.id)
        delete_item_id.delete(synchronize_session=False)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "Poprawnie usunięto technologie!"})
    except(Exception):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Błąd podczas usuwania technologii!"})
