import uuid

from core.repository.psql.users.one import one_by_id_psql, one_by_login_psql
from tests.core.repository.psql.users.helper import create_test_user


class TestOneByLoginPsql:
    def test_one_by_login01_returns_ok(self, db_session):
        user = create_test_user(db_session, login="alice")

        result, err, ok = one_by_login_psql("alice", db_session=db_session)

        assert ok is True and err is None
        assert result.id == str(user.id)

    def test_one_by_login02_not_found_returns_error(self, db_session):
        result, err, ok = one_by_login_psql("does-not-exist", db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"


class TestOneByIdPsql:
    def test_one_by_id01_returns_ok(self, db_session):
        user = create_test_user(db_session, login="bob")

        result, err, ok = one_by_id_psql(str(user.id), db_session=db_session)

        assert ok is True and err is None
        assert result.login == "bob"

    def test_one_by_id02_not_found_returns_error(self, db_session):
        result, err, ok = one_by_id_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"
