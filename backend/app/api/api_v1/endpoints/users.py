"""
User management endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str


@router.get("/me", response_model=User)
async def get_current_user():
    """Get current user - simplified for demo."""
    return User(
        id="demo-user-123",
        email="demo@playbookwiz.com",
        name="Demo User",
        role="brand_manager"
    )
