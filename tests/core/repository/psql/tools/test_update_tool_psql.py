import uuid

from core.repository.psql.tools.images.attach import attach_tool_image_psql
from core.repository.psql.tools.one import one_tool_by_id_psql
from core.repository.psql.tools.update import update_tool_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.tools.helper import create_test_tool


class TestUpdateToolPsql:
    def test_update01_returns_ok(self, db_session):
        tool = create_test_tool(db_session)

        result, err, ok = update_tool_psql(str(tool.id), name="Updated", db_session=db_session)

        assert ok is True and err is None
        assert result.name == "Updated"

    def test_update02_omitted_fields_are_left_untouched(self, db_session):
        tool = create_test_tool(
            db_session,
            name={"pl": "Python", "en": "Python"},
            information={"pl": "Backend language", "en": "Backend language"},
            progress=80,
        )

        result, _, ok = update_tool_psql(str(tool.id), name="Python3", db_session=db_session)

        assert ok is True
        assert result.name == "Python3"
        assert result.information == "Backend language"
        assert result.progress == 80

    def test_update03_explicit_none_clears_only_that_language(self, db_session):
        tool = create_test_tool(db_session, information={"pl": "Opis PL", "en": "Description EN"})

        result, _, ok = update_tool_psql(str(tool.id), information=None, db_session=db_session)

        assert ok is True
        assert result.information is None  # pl (domyślny język) wyczyszczony — nic do pokazania
        assert tool.information == {"en": "Description EN"}  # en zostaje nietknięte w JSONB

    def test_update04_name_cannot_be_cleared(self, db_session):
        tool = create_test_tool(db_session)

        _, err, ok = update_tool_psql(str(tool.id), name=None, db_session=db_session)

        assert ok is False
        assert err.key_type_error == "InvalidValue"

    def test_update05_edits_one_language_without_touching_the_other(self, db_session):
        tool = create_test_tool(db_session, name={"pl": "Wąż", "en": "Snake"})

        result, _, ok = update_tool_psql(
            str(tool.id), language_code="en", name="Python Snake", db_session=db_session
        )

        assert ok is True
        assert result.name == "Python Snake"  # odpowiedź rozwiązana dla edytowanego języka (en)
        pl_view, _, _ = one_tool_by_id_psql(str(tool.id), lang="pl", db_session=db_session)
        assert pl_view.name == "Wąż"  # pl bez zmian

    def test_update06_keeps_attached_images_in_response(self, db_session):
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)
        attach_tool_image_psql(str(tool.id), str(file.id), sort_order=0, db_session=db_session)

        result, _, ok = update_tool_psql(str(tool.id), name="Updated", db_session=db_session)

        assert ok is True
        assert len(result.images) == 1
        assert result.images[0].file_id == str(file.id)

    def test_update07_nonexistent_returns_not_found(self, db_session):
        result, err, ok = update_tool_psql(str(uuid.uuid4()), name="X", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
