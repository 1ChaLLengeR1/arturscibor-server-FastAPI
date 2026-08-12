import jwt as pyjwt
from sqlalchemy.orm import Session

from api.response import ApiErrorData
from core.common.jwt import create_access_token, create_refresh_token, decode_refresh_token
from core.handler.auth.response import AuthTokensResult
from core.repository.psql.users.one import one_by_id_psql


def handler_refresh(
    id_user: str, refresh_token: str, db_session: Session | None = None
) -> tuple[AuthTokensResult | None, ApiErrorData | None, bool]:
    invalid_token = ApiErrorData(
        message="Invalid refresh token",
        type_module="handler_refresh",
        type_error="unauthorized",
        key_type_error="Exception",
    )

    try:
        user, _, ok = one_by_id_psql(id_user, db_session=db_session)
        if not ok:
            return None, invalid_token, False

        try:
            payload = decode_refresh_token(refresh_token)
        except pyjwt.PyJWTError:
            return None, invalid_token, False

        if payload.get("sub") != user.id:
            return None, invalid_token, False

        return (
            AuthTokensResult(
                id_user=user.id,
                type=user.type,
                access_token=create_access_token(user.id),
                refresh_token=create_refresh_token(user.id),
            ),
            None,
            True,
        )
    except Exception as e:
        return (
            None,
            ApiErrorData(
                message=str(e),
                type_module="handler_refresh",
                type_error="exception",
                key_type_error="Exception",
            ),
            False,
        )
