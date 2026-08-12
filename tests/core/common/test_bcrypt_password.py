from core.common.bcrypt_password import hash_password, verify_password


class TestBcryptPassword:
    def test_bcrypt01_verify_correct_password_returns_true(self):
        hashed = hash_password("secret123")

        assert verify_password("secret123", hashed) is True

    def test_bcrypt02_verify_wrong_password_returns_false(self):
        hashed = hash_password("secret123")

        assert verify_password("wrong-password", hashed) is False

    def test_bcrypt03_hash_is_not_plaintext(self):
        hashed = hash_password("secret123")

        assert hashed != "secret123"
