"""
Authentication endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint - simplified for demo."""
    # This is a simplified implementation for demo purposes
    if request.email == "demo@playbookwiz.com" and request.password == "demo123":
        return LoginResponse(
            access_token="demo-token-123",
            token_type="bearer",
            expires_in=3600
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


@router.post("/logout")
async def logout():
    """Logout endpoint."""
    return {"message": "Successfully logged out"}
