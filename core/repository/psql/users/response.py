from dataclasses import dataclass

from database.psql.models.users import Users


@dataclass
class UserResponse:
    id: str
    login: str
    password: str
    type: str


def _to_user_response(model: Users) -> UserResponse:
    return UserResponse(id=str(model.id), login=model.login, password=model.password, type=model.type)
