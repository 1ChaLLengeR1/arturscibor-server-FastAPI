import uuid

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.work.items.delete import router as admin_work_item_delete_router
from api.endpoints.urls import ADMIN_WORK_ITEM_DELETE
from core.common.jwt import create_access_token
from database.psql.models.work import WorkItem
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


class TestApiAdminDeleteWorkItem:
    def test_delete01_returns_200(self, db_session):
        client = make_client(db_session, admin_work_item_delete_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        response = client.delete(
            ADMIN_WORK_ITEM_DELETE.format(work_id=work.id, item_id=item.id), headers=headers
        )

        assert response.status_code == 200

    def test_delete02_row_removed_from_db(self, db_session):
        client = make_client(db_session, admin_work_item_delete_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        client.delete(ADMIN_WORK_ITEM_DELETE.format(work_id=work.id, item_id=item.id), headers=headers)

        assert db_session.query(WorkItem).filter(WorkItem.id == item.id).first() is None

    def test_delete03_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, admin_work_item_delete_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)

        response = client.delete(
            ADMIN_WORK_ITEM_DELETE.format(work_id=work.id, item_id=uuid.uuid4()), headers=headers
        )

        assert response.status_code == 404

    def test_delete04_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_work_item_delete_router)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        response = client.delete(ADMIN_WORK_ITEM_DELETE.format(work_id=work.id, item_id=item.id))

        assert response.status_code == 401

    def test_delete05_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_work_item_delete_router)
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.delete(
            ADMIN_WORK_ITEM_DELETE.format(work_id=work.id, item_id=item.id),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
