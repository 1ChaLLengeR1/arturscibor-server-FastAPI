import uuid

from core.repository.psql.tools.images.attach import attach_tool_image_psql
from core.repository.psql.tools.one import one_tool_by_id_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.tools.helper import create_test_tool


class TestOneToolByIdPsql:
    def test_one01_returns_tool(self, db_session):
        tool = create_test_tool(db_session)

        result, err, ok = one_tool_by_id_psql(str(tool.id), db_session=db_session)

        assert ok is True and err is None
        assert result.id == str(tool.id)

    def test_one02_no_images_returns_empty_list(self, db_session):
        tool = create_test_tool(db_session)

        result, _, ok = one_tool_by_id_psql(str(tool.id), db_session=db_session)

        assert ok is True
        assert result.images == []

    def test_one03_returns_attached_images_ordered_by_sort_order(self, db_session):
        tool = create_test_tool(db_session)
        second = create_test_file(db_session, name="second.png")
        first = create_test_file(db_session, name="first.png")
        attach_tool_image_psql(str(tool.id), str(second.id), sort_order=1, db_session=db_session)
        attach_tool_image_psql(str(tool.id), str(first.id), sort_order=0, db_session=db_session)

        result, _, ok = one_tool_by_id_psql(str(tool.id), db_session=db_session)

        assert ok is True
        assert [image.file_id for image in result.images] == [str(first.id), str(second.id)]

    def test_one04_nonexistent_returns_not_found(self, db_session):
        result, err, ok = one_tool_by_id_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"
