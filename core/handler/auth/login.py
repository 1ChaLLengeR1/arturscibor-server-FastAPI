from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.common.bcrypt_password import verify_password
from core.common.jwt import create_access_token, create_refresh_token
from core.handler.auth.response import AuthTokensResult
from core.repository.psql.users.one_by_login import one_by_login_psql


def handler_login(
    login: str, password: str, db_session: Session | None = None
) -> tuple[AuthTokensResult | None, ApiErrorData | None, bool]:
    invalid_credentials = ApiErrorData(
        message="Invalid login or password",
        type_module="handler_login",
        type_error="unauthorized",
        key_type_error="NotFound",
    )

    try:
        user, _, ok = one_by_login_psql(login, db_session=db_session)
        if not ok:
            return None, invalid_credentials, False

        if not verify_password(password, user.password):
            return None, invalid_credentials, False

        return (
            AuthTokensResult(
                id_user=user.id,
                type=user.type,
                access_token=create_access_token(user.id, extra_claims={"role": user.type}),
                refresh_token=create_refresh_token(user.id, extra_claims={"role": user.type}),
            ),
            None,
            True,
        )
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_login",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
