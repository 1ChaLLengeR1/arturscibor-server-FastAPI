from core.repository.psql.tools.images.attach import attach_tool_image_psql
from database.psql.models.tools import ToolImage
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.tools.helper import create_test_tool


class TestAttachToolImagePsql:
    def test_attach01_returns_ok(self, db_session):
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)

        _, err, ok = attach_tool_image_psql(str(tool.id), str(file.id), sort_order=0, db_session=db_session)

        assert ok is True and err is None

    def test_attach02_row_persisted_with_sort_order(self, db_session):
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)

        attach_tool_image_psql(str(tool.id), str(file.id), sort_order=3, db_session=db_session)

        image = db_session.query(ToolImage).filter(ToolImage.file_id == file.id).first()
        assert image is not None
        assert image.tool_id == tool.id
        assert image.sort_order == 3

    def test_attach03_same_file_twice_returns_conflict(self, db_session):
        tool = create_test_tool(db_session)
        other_tool = create_test_tool(db_session, name={"pl": "Other", "en": "Other"})
        file = create_test_file(db_session)
        attach_tool_image_psql(str(tool.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = attach_tool_image_psql(str(other_tool.id), str(file.id), sort_order=0, db_session=db_session)

        assert ok is False
        assert err.key_type_error == "AlreadyAttached"
