"""
API dependencies.
"""

from fastapi import HTTPException, status
from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str


async def get_current_user() -> User:
    """Get current user - simplified for demo."""
    # This is a simplified implementation for demo purposes
    return User(
        id="demo-user-123",
        email="demo@playbookwiz.com", 
        name="Demo User",
        role="brand_manager"
    )
