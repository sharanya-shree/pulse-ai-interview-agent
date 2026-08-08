import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def cleanup_sqlite_db():
    """Cleanup SQLite test database file after running the test suite."""
    yield
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except Exception:
            pass


@pytest.fixture
def client():
    """Pytest fixture providing a TestClient instance for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client
