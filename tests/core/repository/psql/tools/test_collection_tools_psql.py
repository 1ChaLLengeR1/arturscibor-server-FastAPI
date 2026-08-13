from core.repository.psql.tools.collection import collection_tools_psql
from core.repository.psql.tools.images.attach import attach_tool_image_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.tools.helper import create_test_tool


class TestCollectionToolsPsql:
    def test_collection01_empty_returns_empty_list(self, db_session):
        result, err, ok = collection_tools_psql(db_session=db_session)

        assert ok is True and err is None
        assert result == []

    def test_collection02_returns_all_tools(self, db_session):
        create_test_tool(db_session, name={"pl": "Python", "en": "Python"}, numeric=1)
        create_test_tool(db_session, name={"pl": "Rust", "en": "Rust"}, numeric=2)

        result, _, ok = collection_tools_psql(db_session=db_session)

        assert ok is True
        assert len(result) == 2

    def test_collection03_ordered_by_numeric_ascending(self, db_session):
        create_test_tool(db_session, name={"pl": "Second", "en": "Second"}, numeric=2)
        create_test_tool(db_session, name={"pl": "First", "en": "First"}, numeric=1)

        result, _, ok = collection_tools_psql(db_session=db_session)

        assert ok is True
        assert [tool.name for tool in result] == ["First", "Second"]

    def test_collection04_null_numeric_sorted_last(self, db_session):
        create_test_tool(db_session, name={"pl": "NoOrder", "en": "NoOrder"}, numeric=None)
        create_test_tool(db_session, name={"pl": "First", "en": "First"}, numeric=1)

        result, _, ok = collection_tools_psql(db_session=db_session)

        assert ok is True
        assert [tool.name for tool in result] == ["First", "NoOrder"]

    def test_collection05_includes_images_per_tool(self, db_session):
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)
        attach_tool_image_psql(str(tool.id), str(file.id), sort_order=0, db_session=db_session)

        result, _, ok = collection_tools_psql(db_session=db_session)

        assert ok is True
        assert len(result[0].images) == 1
        assert result[0].images[0].file_id == str(file.id)

    def test_collection06_resolves_requested_language_per_tool(self, db_session):
        create_test_tool(db_session, name={"pl": "Wąż", "en": "Snake"}, numeric=1)

        result, _, ok = collection_tools_psql(lang="en", db_session=db_session)

        assert ok is True
        assert result[0].name == "Snake"
