from datetime import datetime, timedelta
import jwt
from decouple import config
from typing import Union, Any
from pydantic import ValidationError


def create_access_token(user: Union[str, Any]):
    expire_delta = datetime.utcnow() + timedelta(hours=int(config("ACCESS_TOKEN_EXPIRE_HOURS")))
    to_encode = {"exp": expire_delta, "sub": str(user)}
    jwt_encoded = jwt.encode(to_encode, config("SECRET_ADMIN_TOKEN"), config("ALGORITHM"))
    return jwt_encoded


def create_refresh_token(user: Union[str, Any]):
    expire_delta = datetime.utcnow() + timedelta(hours=int(config("REFRESH_TOKEN_EXPIRE_HOURS")))
    to_encode = {"exp": expire_delta, "sub": str(user)}
    jwt_encoded = jwt.encode(to_encode, config("REFRESH_ADMIN_TOKEN"), config("ALGORITHM"))
    return jwt_encoded


def check_refresh_token(token: str, user: Union[str, Any]):
    try:
        if not token:
            return {"error": "Brak Tokenu!"}

        jwt.decode(token, config("REFRESH_ADMIN_TOKEN"), config("ALGORITHM"))
        return {"access_token": create_access_token(user)}

    except(jwt.PyJWTError, ValidationError):
        return {"error": "Token nie jest poprawny!"}
