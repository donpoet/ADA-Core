from fastapi.testclient import TestClient
from app.main import app

def test_info_endpoint():
    client = TestClient(app)
    response = client.get("/info")

    assert response.status_code == 200
        
    data = response.json()

    assert data["name"] == "ADA Core"
    assert data["version"] is not None