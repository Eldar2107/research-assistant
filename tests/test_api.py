from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health_check():
    """Health check endpoint-inin işlədiyini yoxlayırıq"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_search_endpoint_mock(monkeypatch):
    """Search endpoint-ini yoxlayırıq (monkeypatch istifadə edərək)"""
    
    # Asinxron funksiyanı simulyasiya edirik
    async def mock_answer(query):
        return {"answer": "Test synthetic answer", "sources": []}

    # src.api daxilindəki answer_question funksiyasını əvəz edirik
    monkeypatch.setattr("src.api.answer_question", mock_answer)
    
    response = client.post("/api/search", json={"query": "quantum computing"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["query"] == "quantum computing"
    assert "answer" in data