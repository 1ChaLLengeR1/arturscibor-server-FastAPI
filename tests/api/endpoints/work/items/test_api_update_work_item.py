import uuid

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.work.items.update import router as admin_work_item_update_router
from api.endpoints.urls import ADMIN_WORK_ITEM_UPDATE
from core.common.jwt import create_access_token
from tests.api.endpoints.work.helper import admin_auth_headers, make_client
from tests.core.repository.psql.users.helper import create_test_user
from tests.core.repository.psql.work.helper import create_test_work
from tests.core.repository.psql.work.items.helper import create_test_work_item


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminUpdateWorkItem:
    def test_update01_returns_200(self, db_session):
        client = make_client(db_session, admin_work_item_update_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        response = client.put(
            ADMIN_WORK_ITEM_UPDATE.format(work_id=work.id, item_id=item.id),
            json={"title": "Updated Title"},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Title"

    def test_update02_language_code_edits_only_that_language(self, db_session):
        client = make_client(db_session, admin_work_item_update_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id, title={"pl": "Programista", "en": "Developer"})

        response = client.put(
            ADMIN_WORK_ITEM_UPDATE.format(work_id=work.id, item_id=item.id),
            json={"language_code": "en", "title": "Backend Developer"},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Backend Developer"
        assert item.title["pl"] == "Programista"

    def test_update03_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, admin_work_item_update_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)

        response = client.put(
            ADMIN_WORK_ITEM_UPDATE.format(work_id=work.id, item_id=uuid.uuid4()),
            json={"title": "X"},
            headers=headers,
        )

        assert response.status_code == 404

    def test_update04_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_work_item_update_router)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        response = client.put(
            ADMIN_WORK_ITEM_UPDATE.format(work_id=work.id, item_id=item.id), json={"title": "X"}
        )

        assert response.status_code == 401

    def test_update05_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_work_item_update_router)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.put(
            ADMIN_WORK_ITEM_UPDATE.format(work_id=work.id, item_id=item.id),
            json={"title": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
