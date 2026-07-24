from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World from IPO Insight API"}
    print("Backend test passed:", response.json())

if __name__ == "__main__":
    test_read_root()
