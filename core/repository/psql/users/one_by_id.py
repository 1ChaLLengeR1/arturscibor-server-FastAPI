from sqlalchemy import select
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.repository.psql.users.response import UserResponse, _to_user_response
from database.psql.database import managed_session
from database.psql.models.users import Users


def one_by_id_psql(
    id_user: str, db_session: Session | None = None
) -> tuple[UserResponse | None, ApiErrorData | None, bool]:
    try:
        with managed_session(db_session) as (db, _):
            user = db.execute(select(Users).where(Users.id == id_user)).scalar_one_or_none()
            if user is None:
                return (
                    None,
                    ApiErrorData(
                        message="User not found",
                        type_module="one_by_id_psql",
                        type_error="not_found",
                        key_type_error="NotFound",
                    ),
                    False,
                )
            return _to_user_response(user), None, True
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="one_by_id_psql",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
