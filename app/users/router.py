
"""
FastAPI router for user operations.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.users.models import User, UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    email: str

class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    username: str
    email: str
    is_active: bool

    class Config:
        """Pydantic config."""
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
async def get_users():
    """Get all users."""
    return user_service.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    """Get a user by ID."""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    try:
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_data: UserCreate):
    """Update a user."""
    user = user_service.update_user(
        user_id,
        username=user_data.username,
        email=user_data.email
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: UUID):
    """Delete a user."""
    if not user_service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.get("/active/", response_model=List[UserResponse])
async def get_active_users():
    """Get all active users."""
    return user_service.get_active_users()

@router.get("/domain/{domain}", response_model=List[UserResponse])
async def get_users_by_domain(domain: str):
    """Get users by email domain."""
    return user_service.get_users_by_email_domain(domain) 
