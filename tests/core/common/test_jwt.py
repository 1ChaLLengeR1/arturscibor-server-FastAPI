import jwt as pyjwt
import pytest

from core.common.jwt import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token


class TestAccessToken:
    def test_access_token01_roundtrip(self):
        token = create_access_token("user-123")

        payload = decode_access_token(token)

        assert payload["sub"] == "user-123"

    def test_access_token02_extra_claims_included(self):
        token = create_access_token("user-123", extra_claims={"role": "admin"})

        payload = decode_access_token(token)

        assert payload["role"] == "admin"

    def test_access_token03_refresh_token_rejected_as_access_token(self):
        token = create_refresh_token("user-123")

        with pytest.raises(pyjwt.PyJWTError):
            decode_access_token(token)


class TestRefreshToken:
    def test_refresh_token01_roundtrip(self):
        token = create_refresh_token("user-123")

        payload = decode_refresh_token(token)

        assert payload["sub"] == "user-123"
