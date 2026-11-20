
import os

os.environ["SECRET_KEY"] = "test-secret-key"

from app import app


def test_health_endpoint():
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
