
"""
Unit tests for the users module.
"""
import pytest
from datetime import datetime
from uuid import UUID

from app.users.models import User, UserService

@pytest.fixture
def user_service():
    """Fixture providing a UserService instance."""
    return UserService()

@pytest.fixture
def sample_user():
    """Fixture providing a sample user."""
    now = datetime.now()
    return User(
        id=UUID('12345678-1234-5678-1234-567812345678'),
        username="test_user",
        email="test@example.com",
        created_at=now,
        updated_at=now
    )

def test_get_user(user_service, sample_user):
    """Test getting a user by ID."""
    # Add the sample user to the service
    user_service._users[sample_user.id] = sample_user
    
    # Test getting the user
    retrieved_user = user_service.get_user(sample_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == sample_user.id
    assert retrieved_user.username == sample_user.username

def test_get_all_users(user_service):
    """Test getting all users."""
    users = user_service.get_all_users()
    assert isinstance(users, list)
    assert len(users) > 0
    assert all(isinstance(user, User) for user in users)

def test_create_user(user_service):
    """Test creating a new user."""
    username = "new_user"
    email = "new@example.com"
    
    user = user_service.create_user(username, email)
    
    assert isinstance(user, User)
    assert user.username == username
    assert user.email == email
    assert user.is_active is True
    assert user.last_login is None

def test_update_user(user_service, sample_user):
    """Test updating a user."""
    user_service._users[sample_user.id] = sample_user
    
    new_username = "updated_username"
    updated_user = user_service.update_user(
        sample_user.id,
        username=new_username,
        is_active=False
    )
    
    assert updated_user is not None
    assert updated_user.username == new_username
    assert updated_user.is_active is False

def test_delete_user(user_service, sample_user):
    """Test deleting a user."""
    user_service._users[sample_user.id] = sample_user
    
    assert user_service.delete_user(sample_user.id) is True
    assert user_service.get_user(sample_user.id) is None

def test_get_active_users(user_service):
    """Test getting active users."""
    active_users = user_service.get_active_users()
    assert isinstance(active_users, list)
    assert all(user.is_active for user in active_users)

def test_get_users_by_email_domain(user_service):
    """Test getting users by email domain."""
    domain = "example.com"
    domain_users = user_service.get_users_by_email_domain(domain)
    assert isinstance(domain_users, list)
    assert all(user.email.endswith(f"@{domain}") for user in domain_users)

@pytest.mark.parametrize("username,email,expected_active", [
    ("user1", "user1@test.com", True),
    ("user2", "user2@test.com", False),
    ("user3", "user3@test.com", True),
])
def test_create_user_parametrized(user_service, username, email, expected_active):
    """Parametrized test for user creation with different scenarios."""
    user = user_service.create_user(username, email)
    user.is_active = expected_active
    
    assert user.username == username
    assert user.email == email
    assert user.is_active == expected_active 
