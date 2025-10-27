import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original activities
    original = activities.copy()
    yield
    # Restore original activities after test
    activities.clear()
    activities.update(original)

def test_get_activities(client):
    """Test GET /activities endpoint"""
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()

def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]

def test_signup_already_registered(client):
    """Test signup when already registered"""
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Try to signup again
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/NonExistent/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_success(client):
    """Test successful unregistration from activity"""
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Then unregister
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    assert "test@mergington.edu" not in activities["Chess Club"]["participants"]
    assert "Unregistered" in response.json()["message"]

def test_unregister_not_registered(client):
    """Test unregistration when not registered"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Student not found" in response.json()["detail"]

def test_unregister_activity_not_found(client):
    """Test unregistration from non-existent activity"""
    response = client.delete(
        "/activities/NonExistent/participants",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]