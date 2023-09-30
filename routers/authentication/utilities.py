from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
def verification_password(password: str, has_password:str):
    return pwd_context.verify(password, has_password)