import uuid

from core.repository.psql.aboutme.images.attach import attach_about_me_image_psql
from core.repository.psql.aboutme.images.one import one_about_me_image_psql
from tests.core.repository.psql.aboutme.helper import create_test_about_me
from tests.core.repository.psql.file.helper import create_test_file


class TestOneAboutMeImagePsql:
    def test_one01_returns_ok_when_attached(self, db_session):
        about_me = create_test_about_me(db_session)
        file = create_test_file(db_session)
        attach_about_me_image_psql(str(about_me.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = one_about_me_image_psql(str(about_me.id), str(file.id), db_session=db_session)

        assert ok is True and err is None

    def test_one02_not_attached_returns_not_found(self, db_session):
        about_me = create_test_about_me(db_session)
        file = create_test_file(db_session)

        _, err, ok = one_about_me_image_psql(str(about_me.id), str(file.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_one03_nonexistent_file_returns_not_found(self, db_session):
        about_me = create_test_about_me(db_session)

        _, err, ok = one_about_me_image_psql(str(about_me.id), str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
