import uuid

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.work.items.create import router as admin_work_item_create_router
from api.endpoints.urls import ADMIN_WORK_ITEM_CREATE
from core.common.jwt import create_access_token
from tests.api.endpoints.work.helper import admin_auth_headers, make_client
from tests.core.repository.psql.users.helper import create_test_user
from tests.core.repository.psql.work.helper import create_test_work


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminCreateWorkItem:
    def test_create01_returns_201(self, db_session):
        client = make_client(db_session, admin_work_item_create_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)

        response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=work.id),
            json={
                "title": {"pl": "Inżynier Oprogramowania", "en": "Software Engineer"},
                "employment_type": "full_time",
                "date_from": "2025-09-01",
                "skills": ["Django", "Redis"],
            },
            headers=headers,
        )

        assert response.status_code == 201
        assert response.json()["data"]["title"] == "Inżynier Oprogramowania"
        assert response.json()["data"]["skills"] == ["Django", "Redis"]

    def test_create02_missing_en_key_returns_422(self, db_session):
        client = make_client(db_session, admin_work_item_create_router)
        headers = admin_auth_headers(db_session)
        work = create_test_work(db_session)

        response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=work.id),
            json={"title": {"pl": "Programista"}},
            headers=headers,
        )

        assert response.status_code == 422

    def test_create03_nonexistent_work_returns_404(self, db_session):
        client = make_client(db_session, admin_work_item_create_router)
        headers = admin_auth_headers(db_session)

        response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=uuid.uuid4()),
            json={"title": {"pl": "Programista", "en": "Developer"}},
            headers=headers,
        )

        assert response.status_code == 404

    def test_create04_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_work_item_create_router)
        work = create_test_work(db_session)

        response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=work.id),
            json={"title": {"pl": "Programista", "en": "Developer"}},
        )

        assert response.status_code == 401

    def test_create05_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_work_item_create_router)
        work = create_test_work(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=work.id),
            json={"title": {"pl": "Programista", "en": "Developer"}},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
