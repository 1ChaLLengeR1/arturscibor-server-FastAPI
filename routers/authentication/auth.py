from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from routers.authentication.schemas import LoginUserSchema, OptionsTokens
from DataBase.db import SessionLocal
from DataBase.models import Users
from routers.authentication.utilities import verification_password
import secrets, json
from JWT.jwt_helper import create_access_token, create_refresh_token, check_refresh_token

router = APIRouter()
db = SessionLocal()


@router.post("/authentication/login", status_code=200)
async def login(payload: LoginUserSchema):
    user = db.query(Users).filter(Users.login == payload.login).first()
    if not user:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Nieprawidłowy login lub hasło!"})

    if not verification_password(payload.password, user.password):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"error": "Nieprawidłowy login lub hasło!"})

    if not user.type == "administrator":
        return {
            "access_token": secrets.token_hex(220),
            "refresh_token": secrets.token_hex(220),
            "id_user": user.id,
            "type": user.type
        }

    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "id_user": user.id,
        "type": user.type
    }


@router.post("/authentication/automaticallyLogin", status_code=200)
async def autoLogin(payload: OptionsTokens):
    user = db.query(Users).filter(Users.id == payload.id_user).first()
    if user is None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Brak użykownika!"})

    token = json.dumps(check_refresh_token(payload.refresh_token, user))
    response = json.loads(token)

    try:
        if response["error"]:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": response["error"]})
    except:
        return {
            "id_user": user.id,
            "access_token": response["access_token"],
            "refresh_token": create_refresh_token(user),
            "type": user.type

        }
