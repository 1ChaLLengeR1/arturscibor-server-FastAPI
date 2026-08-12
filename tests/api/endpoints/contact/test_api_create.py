from api.endpoints.contact.create import router as contact_create_router
from tests.api.endpoints.contact.helper import make_client


class TestApiCreateContact:
    def test_create01_returns_created_message(self, db_session):
        client = make_client(db_session, contact_create_router)

        response = client.post(
            "/api/v1/contact/create",
            json={"name": "Alice", "email": "alice@example.com", "description": "Hello there"},
        )

        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Alice"

    def test_create02_invalid_email_returns_422(self, db_session):
        client = make_client(db_session, contact_create_router)

        response = client.post(
            "/api/v1/contact/create",
            json={"name": "Alice", "email": "not-an-email", "description": "Hello there"},
        )

        assert response.status_code == 422
