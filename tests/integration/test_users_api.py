
"""
Integration tests for the users API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import UUID

from app.main import app

client = TestClient(app)

def test_get_users():
    """Test getting all users."""
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

def test_create_user():
    """Test creating a new user."""
    user_data = {
        "username": "test_user",
        "email": "test@example.com"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"]
    assert user["is_active"] is True
    assert UUID(user["id"])  # Verify UUID format

def test_get_user_not_found():
    """Test getting a non-existent user."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404

def test_update_user():
    """Test updating a user."""
    # First create a user
    user_data = {
        "username": "update_test",
        "email": "update@example.com"
    }
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Update the user
    update_data = {
        "username": "updated_username",
        "email": "updated@example.com"
    }
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == update_data["username"]
    assert updated_user["email"] == update_data["email"]

def test_delete_user():
    """Test deleting a user."""
    # First create a user
    user_data = {
        "username": "delete_test",
        "email": "delete@example.com"
    }
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Delete the user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    
    # Verify user is deleted
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_get_active_users():
    """Test getting active users."""
    response = client.get("/users/active/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert all(user["is_active"] for user in users)

def test_get_users_by_domain():
    """Test getting users by email domain."""
    domain = "example.com"
    response = client.get(f"/users/domain/{domain}")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert all(user["email"].endswith(f"@{domain}") for user in users)

def test_create_user_duplicate_test():
    """Test creating a user (duplicate test for verification)."""
    user_data = {
        "username": "async_test",
        "email": "async@example.com"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"] 
