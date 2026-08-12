import uuid

from core.repository.psql.contact.delete import delete_contact_psql
from tests.core.repository.psql.contact.helper import create_test_contact


class TestDeleteContactPsql:
    def test_delete01_returns_ok(self, db_session):
        contact = create_test_contact(db_session)

        result, err, ok = delete_contact_psql(str(contact.id), db_session=db_session)

        assert ok is True and err is None

    def test_delete02_not_found_returns_error(self, db_session):
        result, err, ok = delete_contact_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
