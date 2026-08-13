import uuid

from core.repository.psql.tools.delete import delete_tool_psql
from database.psql.models.tools import Tools
from tests.core.repository.psql.tools.helper import create_test_tool


class TestDeleteToolPsql:
    def test_delete01_returns_ok(self, db_session):
        tool = create_test_tool(db_session)

        _, err, ok = delete_tool_psql(str(tool.id), db_session=db_session)

        assert ok is True and err is None

    def test_delete02_row_removed_from_db(self, db_session):
        tool = create_test_tool(db_session)

        delete_tool_psql(str(tool.id), db_session=db_session)

        assert db_session.query(Tools).filter(Tools.id == tool.id).first() is None

    def test_delete03_nonexistent_returns_not_found(self, db_session):
        _, err, ok = delete_tool_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
