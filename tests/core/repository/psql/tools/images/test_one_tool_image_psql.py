import uuid

from core.repository.psql.tools.images.attach import attach_tool_image_psql
from core.repository.psql.tools.images.one import one_tool_image_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.tools.helper import create_test_tool


class TestOneToolImagePsql:
    def test_one01_returns_ok_when_attached(self, db_session):
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)
        attach_tool_image_psql(str(tool.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = one_tool_image_psql(str(tool.id), str(file.id), db_session=db_session)

        assert ok is True and err is None

    def test_one02_not_attached_returns_not_found(self, db_session):
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)

        _, err, ok = one_tool_image_psql(str(tool.id), str(file.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_one03_attached_to_different_tool_returns_not_found(self, db_session):
        tool = create_test_tool(db_session)
        other_tool = create_test_tool(db_session, name="Other")
        file = create_test_file(db_session)
        attach_tool_image_psql(str(other_tool.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = one_tool_image_psql(str(tool.id), str(file.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_one04_nonexistent_file_returns_not_found(self, db_session):
        tool = create_test_tool(db_session)

        _, err, ok = one_tool_image_psql(str(tool.id), str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
