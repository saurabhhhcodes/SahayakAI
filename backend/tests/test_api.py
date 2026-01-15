import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.main.pedagogy_agent")
def test_query_endpoint(mock_agent):
    """Test the /query endpoint with a mocked agent."""
    # Mock the agent response (Must be an object with .content)
    mock_agent.return_value = MagicMock(content="This is a mocked response.")

    payload = {"text": "How do I teach gravity?"}
    response = client.post("/query", json=payload)

    # Verify Response
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "This is a mocked response."
    assert data["agent"] == "pedagogy"
    
    # Verify Agent was called
    mock_agent.assert_called_once()

def test_pdf_endpoint():
    """Test the PDF generation endpoint."""
    payload = {
        "title": "Test Lesson",
        "content": "This is a test lesson plan."
    }
    response = client.post("/download/pdf", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

def test_invalid_query():
    """Test /query with invalid payload."""
    response = client.post("/query", json={}) # Missing 'text'
    assert response.status_code == 422 # Unprocessable Entity
