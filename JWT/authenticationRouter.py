from datetime import datetime
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from decouple import config
import jwt
from pydantic import ValidationError, BaseModel
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


async def check_bearer_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Brak tokenu!",
                headers={"WWW-Authenticate": "Bearer"},

            )

        payload = jwt.decode(token, config("SECRET_ADMIN_TOKEN"), config("ALGORITHM"))
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token wygasł!",
                headers={"WWW-Authenticate": "Bearer"},
            )


    except(jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token nie jest poprawny!",
            headers={"WWW-Authenticate": "Bearer"},
        )
