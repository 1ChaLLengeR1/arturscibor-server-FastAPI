import uuid

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.tools.update import router as admin_tools_update_router
from api.endpoints.urls import ADMIN_TOOLS_UPDATE
from core.common.jwt import create_access_token
from tests.api.endpoints.tools.helper import admin_auth_headers, make_client
from tests.core.repository.psql.tools.helper import create_test_tool
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminUpdateTool:
    def test_update01_returns_200(self, db_session):
        client = make_client(db_session, admin_tools_update_router)
        tool = create_test_tool(db_session, name="Python")

        response = client.put(
            ADMIN_TOOLS_UPDATE.format(tool_id=tool.id),
            json={"progress": 95},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 200
        assert response.json()["data"]["progress"] == 95
        assert response.json()["data"]["name"] == "Python"

    def test_update02_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, admin_tools_update_router)

        response = client.put(
            ADMIN_TOOLS_UPDATE.format(tool_id=uuid.uuid4()),
            json={"name": "X"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 404

    def test_update03_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_tools_update_router)
        tool = create_test_tool(db_session)

        response = client.put(ADMIN_TOOLS_UPDATE.format(tool_id=tool.id), json={"name": "X"})

        assert response.status_code == 401

    def test_update04_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_tools_update_router)
        tool = create_test_tool(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.put(
            ADMIN_TOOLS_UPDATE.format(tool_id=tool.id),
            json={"name": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
