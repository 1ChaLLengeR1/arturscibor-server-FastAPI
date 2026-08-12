import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.contact.collection import router as admin_contact_collection_router
from api.endpoints.contact.create import router as contact_create_router
from core.common.jwt import create_access_token
from tests.api.endpoints.contact.helper import make_client
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    # The admin collection endpoint is protected by JWTAuthenticationMiddleware,
    # which looks the caller up via a standalone session (see
    # tests/api/middleware/test_authentication.py for why this is needed).
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestAdminContactE2E:
    def test_e2e01_guest_creates_admin_sees_it(self, db_session):
        admin = create_test_user(db_session, login="admin-e2e", type="admin")
        db_session.commit()
        token = create_access_token(str(admin.id))
        client = make_client(db_session, contact_create_router, admin_contact_collection_router)

        create_response = client.post(
            "/api/v1/contact/create",
            json={"name": "Guest", "email": "guest@example.com", "description": "E2E test message"},
        )
        collection_response = client.get(
            "/api/v1/admin/contact/collection", headers={"Authorization": f"Bearer {token}"}
        )

        assert create_response.status_code == 201
        assert collection_response.status_code == 200
        messages = collection_response.json()["data"]
        assert any(m["email"] == "guest@example.com" for m in messages)

    def test_e2e02_guest_cannot_access_collection(self, db_session):
        client = make_client(db_session, admin_contact_collection_router)

        response = client.get("/api/v1/admin/contact/collection")

        assert response.status_code == 401
