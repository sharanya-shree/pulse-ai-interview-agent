import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Pytest fixture providing a TestClient instance for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client
