from fastapi.testclient import TestClient


def test_candidates_endpoint_returns_official_catalog(client: TestClient):
    """Verify the backend exposes the official ABTalks candidate catalog."""
    response = client.get("/api/candidates")
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert isinstance(data["candidates"], list)
    assert len(data["candidates"]) > 0

    first_candidate = data["candidates"][0]
    assert "member" in first_candidate
    assert "id" in first_candidate["member"]
    assert "name" in first_candidate["member"]
