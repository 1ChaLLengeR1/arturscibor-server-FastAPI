from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from JWT.authenticationRouter import check_bearer_token
from routers.Home.schemas import HomePostJobs, HomeDeleteJobs
from DataBase.db import SessionLocal
from DataBase.models import Jobs

router = APIRouter()
db = SessionLocal()


@router.get("/home/jobs/home_get_job")
async def home_get_jobs():
    try:
        all_item = db.query(Jobs).all()
        return all_item
    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas pobierania Jobs z Home_Panel!"})


@router.post("/home/jobs/home_post_job", dependencies=[Depends(check_bearer_token)],
             status_code=status.HTTP_201_CREATED)
async def home_post_jobs(item: HomePostJobs | None):
    try:
        new_item = Jobs(name=item.job)
        db.add(new_item)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Poprawnie dodano job do Home_Panel"})
    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas dodawania job w Home_Panel!"})


@router.delete("/home/jobs/home_delete_job", dependencies=[Depends(check_bearer_token)])
async def home_delete_jobs(item: HomeDeleteJobs | None):
    try:
        delete_item = db.query(Jobs).filter(Jobs.id == item.id)
        item = delete_item.first()
        if not item:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"error": "Brak takiego id!"})

        delete_item.delete(synchronize_session=False)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"success": "Usunięto poprawnie Job!"})

    except():
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Błąd podczas usuwania job w Home_Panel!"})
