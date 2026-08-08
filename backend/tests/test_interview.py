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
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0
    assert data["done"] is False


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
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0
    assert data["done"] is False


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


def test_full_interview_flow(client: TestClient):
    """Verify a complete 10-turn technical interview flow resulting in structured feedback."""
    session_id = "session-test-flow-202"
    
    # 1. Initialize session
    init_payload = {
        "sessionId": session_id,
        "candidate": {
            "id": "cand-02",
            "name": "Bob Vance",
            "experienceLevel": "Senior",
            "completedDays": [1, 3, 5, 7, 8, 10, 11, 12, 13]
        }
    }
    response = client.post("/api/interview", json=init_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["done"] is False
    assert len(data["reply"]) > 0

    # 2. Simulate 9 answer turns
    for turn in range(9):
        turn_payload = {
            "sessionId": session_id,
            "message": f"Answer to question {turn + 1}: I configure the local environment with Ollama and QwenCoder."
        }
        response = client.post("/api/interview", json=turn_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["done"] is False
        assert len(data["reply"]) > 0

    # 3. 10th answer turn (should trigger completion and feedback generation)
    final_payload = {
        "sessionId": session_id,
        "message": "Final answer: Deploying with Docker and Kubernetes ensures scalability."
    }
    response = client.post("/api/interview", json=final_payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assert interview is complete
    assert data["done"] is True
    assert "reply" in data
    assert "feedback" in data
    
    # Validate feedback format
    feedback = data["feedback"]
    assert feedback is not None
    assert "summary" in feedback
    assert isinstance(feedback["summary"], str)
    assert "strengths" in feedback
    assert isinstance(feedback["strengths"], list)
    assert len(feedback["strengths"]) > 0
    assert "gaps" in feedback
    assert isinstance(feedback["gaps"], list)
    assert "next" in feedback
    assert isinstance(feedback["next"], list)
