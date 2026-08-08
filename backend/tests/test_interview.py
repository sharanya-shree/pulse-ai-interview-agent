from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Verify backend health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_initial_interview_request(client: TestClient):
    """Verify POST /api/interview for initial session request with candidate payload."""
    payload = {
        "sessionId": "session-test-101",
        "candidate": {
            "id": "cand-01",
            "name": "Alex Smith",
            "experienceLevel": "Intermediate",
            "completedDays": [1, 2, 3, 4]
        }
    }
    response = client.post("/api/interview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["done"] is False
    assert "session-test-101" in data["reply"]


def test_subsequent_interview_request(client: TestClient):
    """Verify POST /api/interview for subsequent session turn with candidate message."""
    payload = {
        "sessionId": "session-test-101",
        "message": "I prefer using asynchronous event queues for high throughput workloads."
    }
    response = client.post("/api/interview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["done"] is False
    assert "session-test-101" in data["reply"]


def test_invalid_interview_request_missing_session_id(client: TestClient):
    """Verify POST /api/interview rejects payloads missing mandatory sessionId."""
    payload = {
        "message": "Hello"
    }
    response = client.post("/api/interview", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_invalid_interview_request_missing_candidate_and_message(client: TestClient):
    """Verify POST /api/interview rejects payloads containing neither candidate nor message."""
    payload = {
        "sessionId": "session-test-999"
    }
    response = client.post("/api/interview", json=payload)
    assert response.status_code == 422
