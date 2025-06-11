
"""
User models and mock data for the users module.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

@dataclass
class User:
    """User model with mock data generation capabilities."""
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None

class UserService:
    """Service class for user operations with mock data."""
    
    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock user data."""
        mock_users = [
            User(
                id=uuid4(),
                username="john_doe",
                email="john@example.com",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_login=datetime.now()
            ),
            User(
                id=uuid4(),
                username="jane_smith",
                email="jane@example.com",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=False
            )
        ]
        for user in mock_users:
            self._users[user.id] = user
    
    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        return self._users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self._users.values())
    
    def create_user(self, username: str, email: str) -> User:
        """Create a new user."""
        now = datetime.now()
        user = User(
            id=uuid4(),
            username=username,
            email=email,
            created_at=now,
            updated_at=now
        )
        self._users[user.id] = user
        return user
    
    def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Update a user's attributes."""
        user = self._users.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            # Always update the updated_at timestamp
            user.updated_at = datetime.now()
        return user
    
    def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return [user for user in self._users.values() if user.is_active]
    
    def get_users_by_email_domain(self, domain: str) -> List[User]:
        """Get users by email domain."""
        return [
            user for user in self._users.values()
            if user.email.endswith(f"@{domain}")
        ] 
