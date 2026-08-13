from core.repository.psql.aboutme.images.attach import attach_about_me_image_psql
from database.psql.models.aboutme import AboutMeImage
from tests.core.repository.psql.aboutme.helper import create_test_about_me
from tests.core.repository.psql.file.helper import create_test_file


class TestAttachAboutMeImagePsql:
    def test_attach01_returns_ok(self, db_session):
        about_me = create_test_about_me(db_session)
        file = create_test_file(db_session)

        _, err, ok = attach_about_me_image_psql(str(about_me.id), str(file.id), sort_order=0, db_session=db_session)

        assert ok is True and err is None

    def test_attach02_row_persisted_with_sort_order(self, db_session):
        about_me = create_test_about_me(db_session)
        file = create_test_file(db_session)

        attach_about_me_image_psql(str(about_me.id), str(file.id), sort_order=3, db_session=db_session)

        image = db_session.query(AboutMeImage).filter(AboutMeImage.file_id == file.id).first()
        assert image is not None
        assert image.about_me_id == about_me.id
        assert image.sort_order == 3

    def test_attach03_same_file_twice_returns_conflict(self, db_session):
        about_me = create_test_about_me(db_session)
        file = create_test_file(db_session)
        attach_about_me_image_psql(str(about_me.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = attach_about_me_image_psql(str(about_me.id), str(file.id), sort_order=1, db_session=db_session)

        assert ok is False
        assert err.key_type_error == "AlreadyAttached"
