import httpx
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app, get_team_graph
from app.security import get_current_user

# Create a mock user for tests
mock_user = {
    "id": "test-id",
    "username": "testuser",
    "name": "Test User",
    "email": "test@example.com"
}

# Override the authentication dependency
def get_mock_current_user():
    return mock_user

app.dependency_overrides[get_current_user] = get_mock_current_user

# Use TestClient for synchronous tests
client = TestClient(app)

@pytest.fixture
def non_mocked_hosts() -> list:
    return ["testserver"]

def test_read_root():
    """Tests the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "BMad Backend is running"}

def test_get_agents_endpoint():
    """Tests the /api/agents endpoint."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert isinstance(data["agents"], list)
    if data["agents"]:
        assert any(agent["id"] == "analyst" for agent in data["agents"])

def test_get_workflows_endpoint():
    """Tests the /api/workflows endpoint."""
    response = client.get("/api/workflows")
    assert response.status_code == 200
    assert response.json() == {"workflows": []}

def test_chat_endpoint():
    """
    Tests the /chat endpoint by overriding the graph dependency.
    """
    # Define a mock message object that has a .content attribute
    class MockMessage:
        def __init__(self, content):
            self.content = content

    # Create a mock graph object
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "messages": [MockMessage("mocked response content")],
        "sender": "analyst",
    }

    # Define the dependency override
    def get_mock_graph():
        return mock_graph

    # Apply the override to the app
    app.dependency_overrides[get_team_graph] = get_mock_graph

    # Make the request using the test client
    response = client.post("/api/chat", json={"session_id": "123", "message": "Hello"})

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["sender"] == "analyst"
    assert data["message"] == "mocked response content"

    # Verify that the mock was called correctly
    mock_graph.invoke.assert_called_once()
    call_args = mock_graph.invoke.call_args[0][0]
    assert call_args["messages"][0].content == "Hello"

    # Clean up the override after the test
    app.dependency_overrides.clear()

